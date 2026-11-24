"""Endpoint storefront cho đăng ký và trang đăng nhập."""

from collections.abc import Awaitable, Callable
from hashlib import sha256
from hmac import compare_digest
import logging
import re
from secrets import token_urlsafe
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.modules.identity.service import RegistrationResult
from app.security.session import STOREFRONT_SESSION_COOKIE
from app.shared.web.rendering import templates

router = APIRouter()
logger = logging.getLogger(__name__)

_BROWSER_COOKIE = "__Host-sobie-registration"
_BROWSER_TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")
_BROWSER_SECONDS = 3600
_NO_STORE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}


def _redirect(location: str) -> RedirectResponse:
    return RedirectResponse(location, status_code=303, headers=_NO_STORE)


def _home(request: Request) -> RedirectResponse:
    return _redirect(request.url_for("root").path)


def _browser_cookie(request: Request) -> str | None:
    value = request.cookies.get(_BROWSER_COOKIE, "")
    return value if _BROWSER_TOKEN.fullmatch(value) else None


def _set_browser_cookie(response: Response, browser: str) -> None:
    response.set_cookie(
        _BROWSER_COOKIE,
        browser,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_BROWSER_SECONDS,
    )


def _csrf_token(browser: str) -> str:
    return sha256(f"registration-csrf:{browser}".encode("ascii")).hexdigest()


def _render_registration(
    request: Request, browser: str | None, result: RegistrationResult
) -> Response:
    if result.location:
        response = _redirect(result.location)
    elif result.stage == "registered":
        response = _redirect(request.url_for("storefront_login").path)
    elif result.stage == "signed_in":
        response = _home(request)
        response.set_cookie(
            STOREFRONT_SESSION_COOKIE, result.session_token, httponly=True, secure=True, samesite="lax"
        )
        response.delete_cookie(_BROWSER_COOKIE, secure=True, httponly=True, samesite="lax")
        return response
    else:
        browser = browser or token_urlsafe(32)
        response = templates.TemplateResponse(
            request,
            "register.html",
            {"result": result, "csrf_token": _csrf_token(browser)},
            status_code=result.status,
            headers=_NO_STORE,
        )
    if browser:
        _set_browser_cookie(response, browser)
    return response


async def _run_registration(
    request: Request,
    browser: str | None,
    action: Callable[[str], Awaitable[RegistrationResult]],
    *,
    csrf_token: str | None = None,
    create_browser: bool = False,
) -> Response:
    if request.state.auth_session is not None:
        return _home(request)

    if csrf_token is not None and (
        browser is None
        or not compare_digest(_csrf_token(browser).encode("ascii"), csrf_token.encode("utf-8"))
    ):
        result = RegistrationResult(
            message="Biểu mẫu đã hết hạn. Vui lòng bắt đầu lại.", status=403
        )
        return _render_registration(request, browser, result)

    if create_browser:
        browser = browser or token_urlsafe(32)
    if browser is None:
        result = RegistrationResult(
            message="Lượt xác minh đã hết hạn. Vui lòng bắt đầu lại.", status=400
        )
        return _render_registration(request, browser, result)

    try:
        result = await action(browser)
    except Exception as exc:
        logger.warning("Registration request failed (%s)", type(exc).__name__)
        result = RegistrationResult(
            message="Dịch vụ xác minh tạm thời không khả dụng. Vui lòng thử lại.", status=503
        )
    return _render_registration(request, browser, result)


@router.get("/register", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 1; 1a (specs/use-cases/identity/UC-01-register-account.md)
async def registration_form(request: Request, restart: str = "") -> Response:
    if request.state.auth_session is not None:
        return _home(request)
    browser = _browser_cookie(request)
    if browser and restart != "1":
        return await _run_registration(request, browser, request.app.state.identity_service.get_registration_stage)
    return _render_registration(request, browser, RegistrationResult())


@router.post("/register/email", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 2–3; E1, E3 (specs/use-cases/identity/UC-01-register-account.md)
async def request_registration_otp(
    request: Request, email: Annotated[str, Form()] = "", csrf_token: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.start_email_registration(browser, email),
        csrf_token=csrf_token,
    )


@router.post("/register/otp/resend", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 4a; E5 (specs/use-cases/identity/UC-01-register-account.md)
async def resend_registration_otp(request: Request, csrf_token: Annotated[str, Form()] = "") -> Response:
    return await _run_registration(
        request, _browser_cookie(request), request.app.state.identity_service.resend_email_challenge, csrf_token=csrf_token
    )


@router.post("/register/otp", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 4–5; E4 (specs/use-cases/identity/UC-01-register-account.md)
async def verify_registration_otp(
    request: Request, otp: Annotated[str, Form()] = "", csrf_token: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.verify_registration_email(browser, otp),
        csrf_token=csrf_token,
    )


@router.post("/register/password", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 6–8; E6, E7 (specs/use-cases/identity/UC-01-register-account.md)
async def create_registration_password(
    request: Request,
    password: Annotated[str, Form()] = "",
    password_confirmation: Annotated[str, Form()] = "",
    csrf_token: Annotated[str, Form()] = "",
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.complete_email_registration(browser, password, password_confirmation),
        csrf_token=csrf_token,
    )


@router.get("/register/google", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 1b.1; E8 (specs/use-cases/identity/UC-01-register-account.md)
async def start_google_registration(request: Request, login: str = "") -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.begin_google_registration(browser, allow_create=login != "1"),
        create_browser=True,
    )


@router.get("/register/google/callback", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 1b.2–5; E1, E6, E8 (specs/use-cases/identity/UC-01-register-account.md)
async def google_registration_callback(
    request: Request, state: str = "", code: str = "", error: str = ""
) -> Response:
    if any(len(request.query_params.getlist(name)) > 1 for name in ("state", "code", "error")):
        return _render_registration(
            request,
            _browser_cookie(request),
            RegistrationResult(message="Không thể xác thực Google. Vui lòng thử lại.", status=400),
        )
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.complete_google_registration(
            browser, state=state, code=code, provider_error=error
        ),
    )


@router.post("/register/google/link/otp", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — E1; UC-02 1d (specs/use-cases/identity/UC-01-register-account.md)
async def confirm_google_link(
    request: Request, otp: Annotated[str, Form()] = "", csrf_token: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.verify_link_and_issue_session(browser, otp),
        csrf_token=csrf_token,
    )


@router.get("/login", response_class=HTMLResponse, name="storefront_login")
# UC-01 Đăng ký tài khoản — Main 8; 1b.5 (specs/use-cases/identity/UC-01-register-account.md)
async def storefront_login_form(request: Request) -> Response:
    if request.state.auth_session is not None:
        return _home(request)

    browser = _browser_cookie(request)
    registered = False
    if browser:
        try:
            registered = await request.app.state.identity_service.consume_registration_success(browser)
        except Exception as exc:
            logger.warning("Registration success notice unavailable (%s)", type(exc).__name__)
    return templates.TemplateResponse(
        request, "login.html", {"registered": registered}, headers=_NO_STORE
    )
