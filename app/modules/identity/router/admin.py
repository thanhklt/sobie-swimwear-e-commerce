"""Endpoint portal để xem, tạo, sửa và khóa tài khoản."""

import logging
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from app.error.exceptions import SessionAccessError
from app.security.session import PORTAL_SESSION_COOKIE
from app.shared.web.rendering import templates

from ..schemas import AccountFormError, AuthenticatedSession, PROFILE_FIELDS, Role
from ..service import AccountService, AdminAccountService
from ._web import (
    _COOKIE_FLAGS,
    _NO_STORE,
    _ROLE_LABELS,
    _check_csrf,
    _protected_page,
    _redirect,
    AccountServiceDep,
    Admin,
    AdminServiceDep,
    Employee,
    Internal,
)
from .account import _account_form, _get_account, _profile_submission

router = APIRouter()
logger = logging.getLogger(__package__)


@router.get("/portal", response_class=HTMLResponse)
async def portal_home(request: Request, actor: Internal) -> Response:
    is_admin = actor.role == Role.ADMIN
    return _protected_page(request, "identity/admin/overview.html", {
        "role_label": _ROLE_LABELS[actor.role],
        "management_route": "admin_accounts" if is_admin else "employee_customers",
        "management_label": "Quản lý tài khoản" if is_admin else "Quản lý khách hàng",
    }, logout_form=True)


async def _account_list(
    request: Request, admin_service: AdminAccountService, *, customers_only: bool, q: str, page: int, error: AccountFormError | None = None,
) -> Response:
    accounts, has_next = await admin_service.search_accounts(
        customers_only=customers_only, search=q.replace('\x00', '').strip()[:255], page=page
    )
    return _protected_page(request, "identity/admin/accounts.html", {
        "accounts": accounts, "has_next": has_next, "page": page, "q": q,
        "customers_only": customers_only, "labels": _ROLE_LABELS,
        "notice": request.query_params.get("notice", ""), "error": error,
    }, 400 if error else 200, logout_form=True)


@router.get("/portal/accounts", response_class=HTMLResponse)
async def admin_accounts(request: Request, admin_service: AdminServiceDep, actor: Admin, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, admin_service, customers_only=False, q=q, page=max(1, min(page, 1000000)))


@router.get("/portal/customers", response_class=HTMLResponse)
async def employee_customers(request: Request, admin_service: AdminServiceDep, actor: Employee, q: str = "", page: int = 1) -> Response:
    return await _account_list(request, admin_service, customers_only=True, q=q, page=max(1, min(page, 1000000)))


@router.get("/portal/customers/{account_key}", response_class=HTMLResponse)
async def employee_customer(request: Request, account_service: AccountServiceDep, account_key: UUID, actor: Employee) -> Response:
    account = await _get_account(account_service, account_key, customers_only=True)
    return _protected_page(request, "identity/admin/customer.html", {"account": account, "fields": PROFILE_FIELDS})


@router.get("/portal/accounts/new", response_class=HTMLResponse)
async def new_account_form(request: Request, actor: Admin) -> Response:
    return _account_form(request, title="Tạo tài khoản", account={}, values={}, roles=list(Role), creating=True)


@router.post("/portal/accounts/new", response_class=HTMLResponse)
async def create_account(request: Request, admin_service: AdminServiceDep, actor: Admin) -> Response:
    fields, password = await _profile_submission(request, include_role=True)
    try:
        await admin_service.create_managed_account(actor, fields, password)
    except AccountFormError as error:
        return _account_form(request, title="Tạo tài khoản", account={}, values=fields,
                             roles=list(Role), creating=True, error=error)
    return _redirect(request.url_for("admin_accounts").path + "?notice=created")


def _edit_account_page(request: Request, account: dict, values: dict, error: AccountFormError | None = None) -> Response:
    roles = () if account["role"] == Role.CUSTOMER else (Role.EMPLOYEE, Role.ADMIN)
    return _account_form(request, title="Sửa tài khoản", account=account, values=values, roles=roles, error=error)


@router.get("/portal/accounts/{account_key}/edit", response_class=HTMLResponse)
async def edit_account_form(request: Request, account_service: AccountServiceDep, account_key: UUID, actor: Admin) -> Response:
    account = await _get_account(account_service, account_key)
    return _edit_account_page(request, account, account)


@router.post("/portal/accounts/{account_key}/edit", response_class=HTMLResponse)
async def save_account_edit(request: Request, admin_service: AdminServiceDep, account_service: AccountServiceDep, account_key: UUID, actor: Admin) -> Response:
    fields, _ = await _profile_submission(request, include_role=True)
    try:
        changed_role = await admin_service.edit_managed_account(actor, account_key, fields)
    except AccountFormError as error:
        account = await _get_account(account_service, account_key)
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


async def _lock_action(
    request: Request, account_key: UUID, actor: AuthenticatedSession,
    admin_service: AdminAccountService, account_service: AccountService, *, locked: bool,
) -> Response:
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
        await admin_service.set_account_lock(actor, account_key, locked=locked)
    except AccountFormError as error:
        if from_accounts:
            return await _account_list(request, admin_service, customers_only=False, q=q, page=page, error=error)
        account = await _get_account(account_service, account_key)
        return _edit_account_page(request, account, account, error)
    if locked and actor.account_key == account_key:
        response = _redirect(request.url_for("portal_login").path + "?locked=1")
        response.delete_cookie(PORTAL_SESSION_COOKIE, **_COOKIE_FLAGS)
        return response
    query["lock"] = "locked" if locked else "unlocked"
    return _redirect(f"{destination}?{urlencode(query)}")


@router.post("/portal/accounts/{account_key}/lock")
async def lock_account(request: Request, admin_service: AdminServiceDep, account_service: AccountServiceDep, account_key: UUID, actor: Internal) -> Response:
    return await _lock_action(request, account_key, actor, admin_service, account_service, locked=True)


@router.post("/portal/accounts/{account_key}/unlock")
async def unlock_account(request: Request, admin_service: AdminServiceDep, account_service: AccountServiceDep, account_key: UUID, actor: Admin) -> Response:
    return await _lock_action(request, account_key, actor, admin_service, account_service, locked=False)
