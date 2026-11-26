"""Endpoint hồ sơ, đổi mật khẩu và trang storefront tạm thời."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app.error.exceptions import SessionAccessError

from ..schemas import AccountFormError, AuthenticatedSession, PROFILE_FIELDS, SessionPortal
from ..service import AccountService
from ._web import (
    _COOKIE_FLAGS,
    _NO_STORE,
    _ROLE_LABELS,
    _SESSION_COOKIES,
    _check_csrf,
    _protected_page,
    _redirect,
    AccountServiceDep,
    Customer,
    Internal,
)

router = APIRouter()


def storefront_identity_home(request: Request) -> Response:
    response = _protected_page(request, "identity/account/home.html", {}, logout_form=True)
    response.headers["Vary"] = "Accept"
    return response


async def _profile_submission(request: Request, *, include_role: bool = False):
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    fields = {key: str(form[key]) for key in PROFILE_FIELDS if key in form}
    if include_role and "role" in form:
        fields["role"] = str(form["role"])
    return fields, str(form.get("password", ""))


async def _get_account(account_service: AccountService, key: UUID, *, customers_only: bool = False):
    account = await account_service.get_account_details(key, customers_only=customers_only)
    if account is None:
        raise HTTPException(status_code=404, headers=_NO_STORE)
    return account


def _account_form(request: Request, *, title: str, account: dict, values: dict, roles=(),
                  creating: bool = False, email_readonly: bool = False,
                  error: AccountFormError | None = None) -> Response:
    return _protected_page(request, "identity/_partials/account_form.html", {
        "title": title, "account": account, "values": values, "fields": PROFILE_FIELDS,
        "roles": roles, "labels": _ROLE_LABELS, "creating": creating,
        "email_readonly": email_readonly,
        "saved": request.method == "GET" and error is None and request.query_params.get("saved") == "1",
        "error": error,
    }, 400 if error else 200, logout_form=request.state.auth_portal == SessionPortal.STOREFRONT)


@router.get("/account/profile", response_class=HTMLResponse)
# UC-04 Main 1–2, AC-2 — Hiển thị email ở dạng chỉ xem.
async def customer_profile(request: Request, account_service: AccountServiceDep, actor: Customer) -> Response:
    account = await _get_account(account_service, actor.account_key, customers_only=True)
    return _account_form(request, title="Hồ sơ khách hàng", account=account, values=account, email_readonly=True)


@router.post("/account/profile", response_class=HTMLResponse)
# UC-04 Main 3–5, E1, E2, AC-2 — Lưu các trường được sửa trên storefront.
async def save_customer_profile(request: Request, account_service: AccountServiceDep, actor: Customer) -> Response:
    fields, _ = await _profile_submission(request)
    try:
        await account_service.update_profile(actor, fields)
    except AccountFormError as error:
        account = await _get_account(account_service, actor.account_key, customers_only=True)
        return _account_form(
            request, title="Hồ sơ khách hàng", account=account, values=fields, email_readonly=True, error=error
        )
    return _redirect(request.url_for("customer_profile").path + "?saved=1")


def _password_page(request: Request, error: AccountFormError | None = None) -> Response:
    return _protected_page(request, "identity/account/password.html", {"error": error}, 400 if error else 200)


@router.get("/account/password", response_class=HTMLResponse)
async def customer_password_form(request: Request, account_service: AccountServiceDep, actor: Customer) -> Response:
    return await _password_form(request, actor, account_service)


@router.get("/portal/password", response_class=HTMLResponse)
async def portal_password_form(request: Request, account_service: AccountServiceDep, actor: Internal) -> Response:
    return await _password_form(request, actor, account_service)


async def _password_form(request: Request, actor: AuthenticatedSession, account_service: AccountService) -> Response:
    account = await _get_account(account_service, actor.account_key)
    if not account["has_password"]:
        raise SessionAccessError(status_code=403)
    return _password_page(request)


async def _save_password(request: Request, actor: AuthenticatedSession, account_service: AccountService) -> Response:
    form = await request.form()
    _check_csrf(request, str(form.get("csrf_token", "")))
    portal = request.state.auth_portal
    try:
        await account_service.change_password(
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
async def customer_password_save(request: Request, account_service: AccountServiceDep, actor: Customer) -> Response:
    return await _save_password(request, actor, account_service)


@router.post("/portal/password", response_class=HTMLResponse)
async def portal_password_save(request: Request, account_service: AccountServiceDep, actor: Internal) -> Response:
    return await _save_password(request, actor, account_service)
