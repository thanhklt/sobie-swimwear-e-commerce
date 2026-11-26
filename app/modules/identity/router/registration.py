"""Endpoint storefront cho đăng ký email và xác thực Google."""

import logging
from collections.abc import Awaitable, Callable
from secrets import token_urlsafe
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, Response

from app.security.origin import has_allowed_origin, origin_rejected
from app.shared.web.rendering import templates

from ..schemas import RegistrationResult, SessionPortal
from ._web import (
    _BROWSER_COOKIE,
    _ORIGIN_FORM_HEADERS,
    _browser_cookie,
    _checkout_requested,
    _home,
    _redirect,
    _set_browser_cookie,
    _set_session_cookie,
    _storefront_destination,
    GoogleServiceDep,
    RegistrationServiceDep,
)

router = APIRouter()
logger = logging.getLogger(__package__)


def _render_registration(
    request: Request, browser: str | None, result: RegistrationResult
) -> Response:
    if result.location:
        response = _redirect(result.location)
    elif result.stage == "registered":
        response = _redirect(request.url_for("storefront_login").path)
    elif result.stage == "signed_in":
        response = _redirect(_storefront_destination(request, result.checkout))
        _set_session_cookie(response, SessionPortal.STOREFRONT, result.session_token)
        response.delete_cookie(_BROWSER_COOKIE, secure=True, httponly=True, samesite="lax")
        return response
    else:
        browser = browser or token_urlsafe(32)
        response = templates.TemplateResponse(
            request,
            "identity/registration/register.html",
            {"result": result},
            status_code=result.status,
            # A native form POST from a no-referrer page would send Origin: null.
            headers=_ORIGIN_FORM_HEADERS,
        )
    if browser:
        _set_browser_cookie(response, browser)
    return response


async def _run_registration(
    request: Request,
    browser: str | None,
    action: Callable[[str], Awaitable[RegistrationResult]],
    *,
    create_browser: bool = False,
) -> Response:
    if request.method == "POST" and not has_allowed_origin(request):
        return origin_rejected()

    if request.state.auth_session is not None:
        return _home(request)

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
async def registration_form(request: Request, registration: RegistrationServiceDep, restart: str = "") -> Response:
    if request.state.auth_session is not None:
        return _home(request)
    browser = _browser_cookie(request)
    if browser and restart != "1":
        return await _run_registration(request, browser, registration.get_registration_stage)
    return _render_registration(request, browser, RegistrationResult())


@router.post("/register/email", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 2–3; E1, E3 (specs/use-cases/identity/UC-01-register-account.md)
async def request_registration_otp(
    request: Request, registration: RegistrationServiceDep, email: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: registration.start_email_registration(browser, email),
    )


@router.post("/register/otp/resend", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 4a; E5 (specs/use-cases/identity/UC-01-register-account.md)
async def resend_registration_otp(request: Request, registration: RegistrationServiceDep) -> Response:
    return await _run_registration(
        request, _browser_cookie(request), registration.resend_email_challenge
    )


@router.post("/register/otp", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 4–5; E4 (specs/use-cases/identity/UC-01-register-account.md)
async def verify_registration_otp(
    request: Request, registration: RegistrationServiceDep, otp: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: registration.verify_registration_email(browser, otp),
    )


@router.post("/register/password", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 6–8; E6, E7 (specs/use-cases/identity/UC-01-register-account.md)
async def create_registration_password(
    request: Request,
    registration: RegistrationServiceDep,
    password: Annotated[str, Form()] = "",
    password_confirmation: Annotated[str, Form()] = "",
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: registration.complete_email_registration(browser, password, password_confirmation),
    )


@router.get("/register/google", response_class=HTMLResponse)
# UC-01 1b.1; UC-02 1a, 1c — Khởi tạo luồng Google và giữ đích checkout nếu có.
async def start_google_registration(request: Request, google: GoogleServiceDep, login: str = "") -> Response:
    checkout = login == "1" and _checkout_requested(request)
    if checkout and request.state.auth_session is not None:
        return _redirect(_storefront_destination(request, checkout))
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: google.begin_google_registration(browser, checkout=checkout),
        create_browser=True,
    )


@router.get("/register/google/callback", response_class=HTMLResponse)
# UC-01 1b.2–5, E1, E6, E8; UC-02 1a, 1c, 1d, E6 — Nhận callback và đặt cookie phiên storefront.
async def google_registration_callback(
    request: Request, google: GoogleServiceDep, state: str = "", code: str = "", error: str = ""
) -> Response:
    if any(len(request.query_params.getlist(name)) > 1 for name in ("state", "code", "error")):
        return _render_registration(
            request,
            _browser_cookie(request),
            RegistrationResult(message="Không thể xác thực Google. Vui lòng thử lại.", status=400),
        )
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: google.complete_google_registration(
            browser, state=state, code=code, provider_error=error
        ),
    )
