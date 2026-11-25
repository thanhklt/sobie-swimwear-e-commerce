"""Endpoint storefront cho đăng ký và trang đăng nhập."""

from collections.abc import Awaitable, Callable
from hashlib import sha256
from hmac import compare_digest
import logging
import re
from secrets import token_urlsafe
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from redis.exceptions import RedisError

from app.error.exceptions import SessionAccessError

from app.modules.identity.service import RegistrationResult
from app.modules.identity.account_details import AccountFormError, PROFILE_FIELDS
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.security.origin import has_allowed_origin, origin_rejected
from app.security.session import PORTAL_SESSION_COOKIE, STOREFRONT_SESSION_COOKIE, require_roles
from app.shared.web.rendering import templates

router = APIRouter(prefix="/api/v1/identity")
logger = logging.getLogger(__name__)

_BROWSER_COOKIE = "__Host-sobie-registration"
_BROWSER_TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")
_BROWSER_SECONDS = 3600
_NO_STORE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}
_ORIGIN_FORM_HEADERS = _NO_STORE | {"Referrer-Policy": "strict-origin"}


def _redirect(location: str) -> RedirectResponse:
    return RedirectResponse(location, status_code=303, headers=_NO_STORE)


def _home(request: Request) -> RedirectResponse:
    return _redirect(request.url_for("root").path)


def _checkout_requested(request: Request) -> bool:
    return request.query_params.getlist("return_to") == [request.url_for("checkout").path]


def _storefront_destination(request: Request, checkout: bool) -> str:
    return request.url_for("checkout" if checkout else "root").path


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
        response = _redirect(_storefront_destination(request, result.checkout))
        _set_session_cookie(response, SessionPortal.STOREFRONT, result.session_token)
        response.delete_cookie(_BROWSER_COOKIE, secure=True, httponly=True, samesite="lax")
        return response
    else:
        browser = browser or token_urlsafe(32)
        response = templates.TemplateResponse(
            request,
            "register.html",
            {"result": result, "google_retry_query": urlencode(
                {"login": "1", "return_to": request.url_for("checkout").path}
                if result.checkout else {"login": "1"}
            )},
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
    request: Request, email: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.start_email_registration(browser, email),
    )


@router.post("/register/otp/resend", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 4a; E5 (specs/use-cases/identity/UC-01-register-account.md)
async def resend_registration_otp(request: Request) -> Response:
    return await _run_registration(
        request, _browser_cookie(request), request.app.state.identity_service.resend_email_challenge
    )


@router.post("/register/otp", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 4–5; E4 (specs/use-cases/identity/UC-01-register-account.md)
async def verify_registration_otp(
    request: Request, otp: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.verify_registration_email(browser, otp),
    )


@router.post("/register/password", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — Main 6–8; E6, E7 (specs/use-cases/identity/UC-01-register-account.md)
async def create_registration_password(
    request: Request,
    password: Annotated[str, Form()] = "",
    password_confirmation: Annotated[str, Form()] = "",
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.complete_email_registration(browser, password, password_confirmation),
    )


@router.get("/register/google", response_class=HTMLResponse)
# UC-01 Đăng ký tài khoản — 1b.1; E8 (specs/use-cases/identity/UC-01-register-account.md)
async def start_google_registration(request: Request, login: str = "") -> Response:
    checkout = login == "1" and _checkout_requested(request)
    if checkout and request.state.auth_session is not None:
        return _redirect(_storefront_destination(request, checkout))
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.begin_google_registration(
            browser, allow_create=login != "1", checkout=checkout
        ),
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
    request: Request, otp: Annotated[str, Form()] = ""
) -> Response:
    return await _run_registration(
        request, _browser_cookie(request),
        lambda browser: request.app.state.identity_service.verify_link_and_issue_session(browser, otp),
    )


# Capture the registration POST routes before adding other Identity endpoints.
registration_post_paths = frozenset(
    route.path for route in router.routes if "POST" in route.methods
)


@router.get("/login", response_class=HTMLResponse, name="storefront_login")
# UC-01 Đăng ký tài khoản — Main 8; 1b.5 (specs/use-cases/identity/UC-01-register-account.md)
async def storefront_login_form(request: Request) -> Response:
    if request.state.auth_session is not None:
        return _redirect(_storefront_destination(request, _checkout_requested(request)))

    browser = _browser_cookie(request)
    registered = False
    if browser:
        try:
            registered = await request.app.state.identity_service.consume_registration_success(browser)
        except Exception as exc:
            logger.warning("Registration success notice unavailable (%s)", type(exc).__name__)
    return _login_page(request, registered=registered)


_COOKIE_FLAGS = {"httponly": True, "secure": True, "samesite": "lax"}
_SESSION_COOKIES = {
    SessionPortal.STOREFRONT: STOREFRONT_SESSION_COOKIE,
    SessionPortal.PORTAL: PORTAL_SESSION_COOKIE,
}


def _set_session_cookie(response: Response, portal: SessionPortal, token: str) -> None:
    response.set_cookie(_SESSION_COOKIES[portal], token, **_COOKIE_FLAGS)


def _protected_page(
    request: Request, template: str, context: dict, status: int = 200, *, logout_form: bool = False
) -> Response:
    browser = _browser_cookie(request) or token_urlsafe(32)
    response = templates.TemplateResponse(
        request, template, context | {"csrf_token": _csrf_token(browser)}, status_code=status,
        headers=_ORIGIN_FORM_HEADERS if logout_form else _NO_STORE,
    )
    _set_browser_cookie(response, browser)
    return response


def storefront_identity_home(request: Request) -> Response:
    response = _protected_page(request, "identity_home.html", {}, logout_form=True)
    response.headers["Vary"] = "Accept"
    return response


def _check_csrf(request: Request, token: str) -> None:
    browser = _browser_cookie(request)
    if not browser or not compare_digest(_csrf_token(browser).encode("ascii"), token.encode("utf-8")):
        raise SessionAccessError(status_code=403)


def _login_page(request: Request, *, registered: bool = False, result: RegistrationResult | None = None,
                identifier: str = "") -> Response:
    result = result or RegistrationResult()
    portal = request.state.auth_portal == SessionPortal.PORTAL
    template = "portal_login.html" if portal else "login.html"
    submit_route = "portal_password_login" if portal else "storefront_password_login"
    checkout = not portal and _checkout_requested(request)
    query = {"return_to": request.url_for("checkout").path} if checkout else {}
    form_action = request.url_for(submit_route).path
    if query:
        form_action += "?" + urlencode(query)
    return templates.TemplateResponse(request, template, {
        "registered": registered, "result": result, "identifier": identifier,
        "portal": portal, "form_action": form_action,
        "google_query": urlencode({"login": "1", **query}),
        "password_changed": request.query_params.get("password_changed") == "1",
        "self_locked": request.query_params.get("locked") == "1",
        "role_changed": request.query_params.get("role_changed") == "1",
    }, status_code=result.status, headers=_ORIGIN_FORM_HEADERS)


@router.get("/portal/login", response_class=HTMLResponse)
async def portal_login(request: Request) -> Response:
    if request.state.auth_session:
        return _redirect(request.url_for("portal_home").path)
    return _login_page(request)


@router.post("/login", response_class=HTMLResponse, name="storefront_password_login")
@router.post("/portal/login", response_class=HTMLResponse, name="portal_password_login")
async def password_login(
    request: Request,
    identifier: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = "",
) -> Response:
    portal = request.state.auth_portal
    home = (
        request.url_for("portal_home").path if portal == SessionPortal.PORTAL
        else _storefront_destination(request, _checkout_requested(request))
    )
    if request.state.auth_session:
        return _redirect(home)
    try:
        result = await request.app.state.identity_service.login_with_password(
            identifier, password, portal, request.client.host if request.client else "unknown"
        )
    except RedisError:
        result = RegistrationResult(message="Dịch vụ đăng nhập tạm thời không khả dụng.", status=503)
    if not result.session_token:
        return _login_page(request, result=result, identifier=identifier[:255])
    response = _redirect(home)
    _set_session_cookie(response, portal, result.session_token)
    return response


login_post_paths = frozenset(
    route.path for route in router.routes
    if route.name in {"storefront_password_login", "portal_password_login"}
)


@router.post("/logout", name="storefront_logout")
@router.post("/portal/logout", name="portal_logout")
async def logout(request: Request) -> Response:
    portal = request.state.auth_portal
    name = _SESSION_COOKIES[portal]
    await request.app.state.identity_service.logout(request.cookies.get(name), portal)
    response = _home(request)
    response.delete_cookie(name, **_COOKIE_FLAGS)
    return response


logout_post_paths = frozenset(
    route.path for route in router.routes if route.name in {"storefront_logout", "portal_logout"}
)


Customer = Annotated[AuthenticatedSession, Depends(require_roles(Role.CUSTOMER, login_route="storefront_login"))]
Admin = Annotated[AuthenticatedSession, Depends(require_roles(Role.ADMIN, login_route="portal_login"))]
Employee = Annotated[AuthenticatedSession, Depends(require_roles(Role.EMPLOYEE, login_route="portal_login"))]
Internal = Annotated[
    AuthenticatedSession, Depends(require_roles(Role.ADMIN, Role.EMPLOYEE, login_route="portal_login"))
]

_ROLE_LABELS = {Role.CUSTOMER: "Khách hàng", Role.EMPLOYEE: "Nhân viên", Role.ADMIN: "Admin"}


async def _profile_submission(request: Request, *, include_role: bool = False):
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    fields = {key: str(form[key]) for key in PROFILE_FIELDS if key in form}
    if include_role and "role" in form:
        fields["role"] = str(form["role"])
    return fields, str(form.get("password", ""))


async def _get_account(request: Request, key: UUID, *, customers_only: bool = False):
    account = await request.app.state.identity_service.get_account_details(key, customers_only=customers_only)
    if account is None:
        raise HTTPException(status_code=404, headers=_NO_STORE)
    return account


def _account_form(request: Request, *, title: str, account: dict, values: dict, roles=(),
                  creating: bool = False, error: AccountFormError | None = None) -> Response:
    return _protected_page(request, "profile.html", {
        "title": title, "account": account, "values": values, "fields": PROFILE_FIELDS,
        "roles": roles, "labels": _ROLE_LABELS, "creating": creating,
        "saved": request.method == "GET" and error is None and request.query_params.get("saved") == "1",
        "error": error,
    }, 400 if error else 200, logout_form=request.state.auth_portal == SessionPortal.STOREFRONT)


@router.get("/portal", response_class=HTMLResponse)
async def portal_home(request: Request, actor: Internal) -> Response:
    is_admin = actor.role == Role.ADMIN
    return _protected_page(request, "portal_overview.html", {
        "role_label": _ROLE_LABELS[actor.role],
        "management_route": "admin_accounts" if is_admin else "employee_customers",
        "management_label": "Quản lý tài khoản" if is_admin else "Quản lý khách hàng",
    }, logout_form=True)


@router.get("/account/profile", response_class=HTMLResponse)
async def customer_profile(request: Request, actor: Customer) -> Response:
    account = await _get_account(request, actor.account_key, customers_only=True)
    return _account_form(request, title="Hồ sơ khách hàng", account=account, values=account)


@router.post("/account/profile", response_class=HTMLResponse)
async def save_customer_profile(request: Request, actor: Customer) -> Response:
    fields, _ = await _profile_submission(request)
    try:
        await request.app.state.identity_service.update_profile(actor, fields)
    except AccountFormError as error:
        account = await _get_account(request, actor.account_key, customers_only=True)
        return _account_form(request, title="Hồ sơ khách hàng", account=account, values=fields, error=error)
    return _redirect(request.url_for("customer_profile").path + "?saved=1")


def _password_page(request: Request, error: AccountFormError | None = None) -> Response:
    return _protected_page(request, "password.html", {"error": error}, 400 if error else 200)


@router.get("/account/password", response_class=HTMLResponse)
async def customer_password_form(request: Request, actor: Customer) -> Response:
    return await _password_form(request, actor)


@router.get("/portal/password", response_class=HTMLResponse)
async def portal_password_form(request: Request, actor: Internal) -> Response:
    return await _password_form(request, actor)


async def _password_form(request: Request, actor: AuthenticatedSession) -> Response:
    account = await _get_account(request, actor.account_key)
    if not account["has_password"]:
        raise SessionAccessError(status_code=403)
    return _password_page(request)


async def _save_password(request: Request, actor: AuthenticatedSession) -> Response:
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    portal = request.state.auth_portal
    try:
        await request.app.state.identity_service.change_password(
            actor, portal, str(form.get("current_password", "")),
            str(form.get("password", "")), str(form.get("password_confirmation", "")),
        )
    except AccountFormError as error:
        return _password_page(request, error)
    route = "portal_login" if portal == SessionPortal.PORTAL else "storefront_login"
    response = _redirect(request.url_for(route).path + "?password_changed=1")
    response.delete_cookie(_SESSION_COOKIES[portal], **_COOKIE_FLAGS)
    return response


@router.post("/account/password", response_class=HTMLResponse)
async def customer_password_save(request: Request, actor: Customer) -> Response:
    return await _save_password(request, actor)


@router.post("/portal/password", response_class=HTMLResponse)
async def portal_password_save(request: Request, actor: Internal) -> Response:
    return await _save_password(request, actor)


async def _account_list(
    request: Request, *, customers_only: bool, q: str, page: int, error: AccountFormError | None = None,
) -> Response:
    accounts, has_next = await request.app.state.identity_service.search_accounts(
        customers_only=customers_only, search=q.replace('\x00', '').strip()[:255], page=page
    )
    return _protected_page(request, "accounts.html", {
        "accounts": accounts, "has_next": has_next, "page": page, "q": q,
        "customers_only": customers_only, "labels": _ROLE_LABELS,
        "notice": request.query_params.get("notice", ""), "error": error,
    }, 400 if error else 200, logout_form=True)


@router.get("/portal/accounts", response_class=HTMLResponse)
async def admin_accounts(request: Request, actor: Admin, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, customers_only=False, q=q, page=max(1, min(page, 1000000)))


@router.get("/portal/customers", response_class=HTMLResponse)
async def employee_customers(request: Request, actor: Employee, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, customers_only=True, q=q, page=max(1, min(page, 1000000)))


@router.get("/portal/customers/{account_key}", response_class=HTMLResponse)
async def employee_customer(request: Request, account_key: UUID, actor: Employee) -> Response:
    account = await _get_account(request, account_key, customers_only=True)
    return _protected_page(request, "customer.html", {"account": account, "fields": PROFILE_FIELDS})


@router.get("/portal/accounts/new", response_class=HTMLResponse)
async def new_account_form(request: Request, actor: Admin) -> Response:
    return _account_form(request, title="Tạo tài khoản", account={}, values={}, roles=list(Role), creating=True)


@router.post("/portal/accounts/new", response_class=HTMLResponse)
async def create_account(request: Request, actor: Admin) -> Response:
    fields, password = await _profile_submission(request, include_role=True)
    try:
        await request.app.state.identity_service.create_managed_account(actor, fields, password)
    except AccountFormError as error:
        return _account_form(request, title="Tạo tài khoản", account={}, values=fields,
                             roles=list(Role), creating=True, error=error)
    return _redirect(request.url_for("admin_accounts").path + "?notice=created")


def _edit_account_page(request: Request, account: dict, values: dict, error: AccountFormError | None = None) -> Response:
    roles = () if account["role"] == Role.CUSTOMER else (Role.EMPLOYEE, Role.ADMIN)
    return _account_form(request, title="Sửa tài khoản", account=account, values=values, roles=roles, error=error)


@router.get("/portal/accounts/{account_key}/edit", response_class=HTMLResponse)
async def edit_account_form(request: Request, account_key: UUID, actor: Admin) -> Response:
    account = await _get_account(request, account_key)
    return _edit_account_page(request, account, account)


@router.post("/portal/accounts/{account_key}/edit", response_class=HTMLResponse)
async def save_account_edit(request: Request, account_key: UUID, actor: Admin) -> Response:
    fields, _ = await _profile_submission(request, include_role=True)
    try:
        changed_role = await request.app.state.identity_service.edit_managed_account(actor, account_key, fields)
    except AccountFormError as error:
        account = await _get_account(request, account_key)
        return _edit_account_page(request, account, account | fields, error)
    except SessionAccessError:
        raise
    except Exception as error:
        logger.warning("Managed account update failed (%s)", type(error).__name__)
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Cập nhật không thành công.",
                "message": "Vui lòng thử lại.",
                "link_path": request.url_for("edit_account_form", account_key=account_key).path,
                "link_label": "Quay lại trang sửa tài khoản",
            },
            status_code=500,
            headers=_NO_STORE,
        )
    if changed_role and account_key == actor.account_key:
        response = _redirect(request.url_for("portal_login").path + "?role_changed=1")
        response.delete_cookie(PORTAL_SESSION_COOKIE, **_COOKIE_FLAGS)
        return response
    return _redirect(request.url_for("edit_account_form", account_key=account_key).path + "?saved=1")


async def _lock_action(request: Request, account_key: UUID, actor: AuthenticatedSession, *, locked: bool) -> Response:
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    is_admin = actor.role == Role.ADMIN
    from_accounts = is_admin and form.get("source") == "accounts"
    query: dict[str, str | int] = {}
    if from_accounts:
        q = str(form.get("q", "")).replace('\x00', '').strip()[:255]
        try:
            page = max(1, min(int(str(form.get("page", "1"))), 1000000))
        except ValueError:
            page = 1
        destination = request.url_for("admin_accounts").path
        query = {"q": q, "page": page}
    else:
        route = "edit_account_form" if is_admin else "employee_customer"
        destination = request.url_for(route, account_key=account_key).path

    if form.get("confirm") != "yes":
        return _redirect(f"{destination}?{urlencode(query)}" if query else destination)
    try:
        await request.app.state.identity_service.set_account_lock(actor, account_key, locked=locked)
    except AccountFormError as error:
        if from_accounts:
            return await _account_list(request, customers_only=False, q=q, page=page, error=error)
        account = await _get_account(request, account_key)
        return _edit_account_page(request, account, account, error)
    if locked and actor.account_key == account_key:
        response = _redirect(request.url_for("portal_login").path + "?locked=1")
        response.delete_cookie(PORTAL_SESSION_COOKIE, **_COOKIE_FLAGS)
        return response
    query["lock"] = "locked" if locked else "unlocked"
    return _redirect(f"{destination}?{urlencode(query)}")


@router.post("/portal/accounts/{account_key}/lock")
async def lock_account(request: Request, account_key: UUID, actor: Internal) -> Response:
    return await _lock_action(request, account_key, actor, locked=True)


@router.post("/portal/accounts/{account_key}/unlock")
async def unlock_account(request: Request, account_key: UUID, actor: Admin) -> Response:
    return await _lock_action(request, account_key, actor, locked=False)
