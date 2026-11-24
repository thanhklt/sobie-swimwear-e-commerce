"""Endpoint storefront cho đăng ký và trang đăng nhập."""

from collections.abc import Awaitable, Callable
from hashlib import sha256
from hmac import compare_digest
import logging
import re
from secrets import token_urlsafe
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from redis.exceptions import RedisError

from app.error.exceptions import SessionAccessError

from app.modules.identity.service import RegistrationResult
from app.modules.identity.account_details import AccountFormError, PROFILE_FIELDS
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.security.session import PORTAL_SESSION_COOKIE, STOREFRONT_SESSION_COOKIE, require_roles
from app.shared.web.rendering import templates

router = APIRouter()
login_router = APIRouter()
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
        _set_session_cookie(response, SessionPortal.STOREFRONT, result.session_token)
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


@router.get("/login", response_class=HTMLResponse, name="legacy_storefront_login", include_in_schema=False)
@login_router.get("/login", response_class=HTMLResponse, name="storefront_login")
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
    return _login_page(request, registered=registered)


_COOKIE_FLAGS = {"httponly": True, "secure": True, "samesite": "lax"}
_SESSION_COOKIES = {
    SessionPortal.STOREFRONT: STOREFRONT_SESSION_COOKIE,
    SessionPortal.PORTAL: PORTAL_SESSION_COOKIE,
}


def _set_session_cookie(response: Response, portal: SessionPortal, token: str) -> None:
    response.set_cookie(_SESSION_COOKIES[portal], token, **_COOKIE_FLAGS)


def _protected_page(request: Request, template: str, context: dict, status: int = 200) -> Response:
    browser = _browser_cookie(request) or token_urlsafe(32)
    response = templates.TemplateResponse(
        request, template, context | {"csrf_token": _csrf_token(browser)}, status_code=status,
        headers=_NO_STORE,
    )
    _set_browser_cookie(response, browser)
    return response


def storefront_identity_home(request: Request) -> Response:
    response = _protected_page(request, "identity_home.html", {})
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
    return _protected_page(request, template, {
        "registered": registered, "result": result, "identifier": identifier,
        "portal": portal, "form_action": request.url_for(submit_route).path,
        "password_changed": request.query_params.get("password_changed") == "1",
        "self_locked": request.query_params.get("locked") == "1",
        "role_changed": request.query_params.get("role_changed") == "1",
    }, result.status)


@router.get("/admin/login", response_class=HTMLResponse, name="legacy_portal_login", include_in_schema=False)
@login_router.get("/admin/login", response_class=HTMLResponse)
async def portal_login(request: Request) -> Response:
    if request.state.auth_session:
        return _redirect(request.url_for("portal_home").path)
    return _login_page(request)


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
@router.post("/admin/login", response_class=HTMLResponse, include_in_schema=False)
@login_router.post("/login", response_class=HTMLResponse, name="storefront_password_login")
@login_router.post("/admin/login", response_class=HTMLResponse, name="portal_password_login")
async def password_login(
    request: Request,
    identifier: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = "",
    csrf_token: Annotated[str, Form()] = "",
) -> Response:
    _check_csrf(request, csrf_token)
    portal = request.state.auth_portal
    home = request.url_for("portal_home").path if portal == SessionPortal.PORTAL else request.url_for("root").path
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


@router.post("/logout", name="storefront_logout")
@router.post("/admin/logout", name="portal_logout")
async def logout(request: Request, csrf_token: Annotated[str, Form()] = "") -> Response:
    _check_csrf(request, csrf_token)
    portal = request.state.auth_portal
    name = _SESSION_COOKIES[portal]
    await request.app.state.identity_service.logout(request.cookies.get(name), portal)
    response = _home(request)
    response.delete_cookie(name, **_COOKIE_FLAGS)
    return response


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
        "saved": request.query_params.get("saved") == "1", "error": error,
    }, 400 if error else 200)


@router.get("/admin", response_class=HTMLResponse)
async def portal_home(request: Request, actor: Internal) -> Response:
    is_admin = actor.role == Role.ADMIN
    return _protected_page(request, "portal_overview.html", {
        "role_label": _ROLE_LABELS[actor.role],
        "management_route": "admin_accounts" if is_admin else "employee_customers",
        "management_label": "Quản lý tài khoản" if is_admin else "Quản lý khách hàng",
    })


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


@router.get("/admin/password", response_class=HTMLResponse)
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


@router.post("/admin/password", response_class=HTMLResponse)
async def portal_password_save(request: Request, actor: Internal) -> Response:
    return await _save_password(request, actor)


async def _account_list(request: Request, *, customers_only: bool, q: str, page: int) -> Response:
    accounts, has_next = await request.app.state.identity_service.search_accounts(
        customers_only=customers_only, search=q.replace('\x00', '').strip()[:255], page=page
    )
    return _protected_page(request, "accounts.html", {
        "accounts": accounts, "has_next": has_next, "page": page, "q": q,
        "customers_only": customers_only, "labels": _ROLE_LABELS,
        "notice": request.query_params.get("notice", ""),
    })


@router.get("/admin/accounts", response_class=HTMLResponse)
async def admin_accounts(request: Request, actor: Admin, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, customers_only=False, q=q, page=max(1, min(page, 1000000)))


@router.get("/admin/customers", response_class=HTMLResponse)
async def employee_customers(request: Request, actor: Employee, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, customers_only=True, q=q, page=max(1, min(page, 1000000)))


@router.get("/admin/customers/{key}", response_class=HTMLResponse)
async def employee_customer(request: Request, key: UUID, actor: Employee) -> Response:
    account = await _get_account(request, key, customers_only=True)
    return _protected_page(request, "customer.html", {"account": account, "fields": PROFILE_FIELDS})


@router.get("/admin/accounts/new", response_class=HTMLResponse)
async def new_account_form(request: Request, actor: Admin) -> Response:
    return _account_form(request, title="Tạo tài khoản", account={}, values={}, roles=list(Role), creating=True)


@router.post("/admin/accounts/new", response_class=HTMLResponse)
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


@router.get("/admin/accounts/{key}/edit", response_class=HTMLResponse)
async def edit_account_form(request: Request, key: UUID, actor: Admin) -> Response:
    account = await _get_account(request, key)
    return _edit_account_page(request, account, account)


@router.post("/admin/accounts/{key}/edit", response_class=HTMLResponse)
async def save_account_edit(request: Request, key: UUID, actor: Admin) -> Response:
    fields, _ = await _profile_submission(request, include_role=True)
    try:
        changed_role = await request.app.state.identity_service.edit_managed_account(actor, key, fields)
    except AccountFormError as error:
        account = await _get_account(request, key)
        return _edit_account_page(request, account, account | fields, error)
    if changed_role and key == actor.account_key:
        response = _redirect(request.url_for("portal_login").path + "?role_changed=1")
        response.delete_cookie(PORTAL_SESSION_COOKIE, **_COOKIE_FLAGS)
        return response
    return _redirect(request.url_for("edit_account_form", key=key).path + "?saved=1")


async def _lock_action(request: Request, key: UUID, actor: AuthenticatedSession, *, locked: bool) -> Response:
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    is_admin = actor.role == Role.ADMIN
    detail = request.url_for("edit_account_form" if is_admin else "employee_customer", key=key).path
    if form.get("confirm") != "yes":
        return _redirect(detail)
    try:
        await request.app.state.identity_service.set_account_lock(actor, key, locked=locked)
    except AccountFormError as error:
        account = await _get_account(request, key)
        return _edit_account_page(request, account, account, error)
    if locked and actor.account_key == key:
        response = _redirect(request.url_for("portal_login").path + "?locked=1")
        response.delete_cookie(PORTAL_SESSION_COOKIE, **_COOKIE_FLAGS)
        return response
    return _redirect(detail + ("?lock=locked" if locked else "?lock=unlocked"))


@router.post("/admin/accounts/{key}/lock")
async def lock_account(request: Request, key: UUID, actor: Internal) -> Response:
    return await _lock_action(request, key, actor, locked=True)


@router.post("/admin/accounts/{key}/unlock")
async def unlock_account(request: Request, key: UUID, actor: Admin) -> Response:
    return await _lock_action(request, key, actor, locked=False)
