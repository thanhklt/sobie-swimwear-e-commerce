"""Cookie, trang được bảo vệ và dependency dùng chung cho router identity."""

import re
from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe
from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse, Response

from app.error.exceptions import SessionAccessError
from app.security.session import PORTAL_SESSION_COOKIE, STOREFRONT_SESSION_COOKIE, require_roles
from app.shared.web.rendering import templates

from ..schemas import AuthenticatedSession, Role, SessionPortal
from ..service import AccountService, AdminAccountService, EmailRegistrationService, GoogleAuthService, SessionService


_BROWSER_COOKIE = "__Host-sobie-registration"
_BROWSER_TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")
_BROWSER_SECONDS = 3600
_NO_STORE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}
_ORIGIN_FORM_HEADERS = _NO_STORE | {"Referrer-Policy": "strict-origin"}
_COOKIE_FLAGS = {"httponly": True, "secure": True, "samesite": "lax"}
_SESSION_COOKIES = {
    SessionPortal.STOREFRONT: STOREFRONT_SESSION_COOKIE,
    SessionPortal.PORTAL: PORTAL_SESSION_COOKIE,
}


Customer = Annotated[AuthenticatedSession, Depends(require_roles(Role.CUSTOMER, login_route="storefront_login"))]
Admin = Annotated[AuthenticatedSession, Depends(require_roles(Role.ADMIN, login_route="portal_login"))]
Employee = Annotated[AuthenticatedSession, Depends(require_roles(Role.EMPLOYEE, login_route="portal_login"))]
Internal = Annotated[
    AuthenticatedSession, Depends(require_roles(Role.ADMIN, Role.EMPLOYEE, login_route="portal_login"))
]

_ROLE_LABELS = {Role.CUSTOMER: "Khách hàng", Role.EMPLOYEE: "Nhân viên", Role.ADMIN: "Admin"}


def _redirect(location: str) -> RedirectResponse:
    return RedirectResponse(location, status_code=303, headers=_NO_STORE)


def _home(request: Request) -> RedirectResponse:
    return _redirect(request.url_for("root").path)


def _checkout_requested(request: Request) -> bool:
    return request.query_params.getlist("return_url") == [request.url_for("checkout").path]


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


def _check_csrf(request: Request, token: str) -> None:
    browser = _browser_cookie(request)
    if not browser or not compare_digest(_csrf_token(browser).encode("ascii"), token.encode("utf-8")):
        raise SessionAccessError(status_code=403)


async def get_sessions_service(request: Request) -> SessionService:
    return request.app.state.identity.sessions


async def get_registration_service(request: Request) -> EmailRegistrationService:
    return request.app.state.identity.registration


async def get_google_service(request: Request) -> GoogleAuthService:
    return request.app.state.identity.google


async def get_account_service(request: Request) -> AccountService:
    return request.app.state.identity.account


async def get_admin_service(request: Request) -> AdminAccountService:
    return request.app.state.identity.admin


SessionServiceDep = Annotated[SessionService, Depends(get_sessions_service)]
RegistrationServiceDep = Annotated[EmailRegistrationService, Depends(get_registration_service)]
GoogleServiceDep = Annotated[GoogleAuthService, Depends(get_google_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
AdminServiceDep = Annotated[AdminAccountService, Depends(get_admin_service)]
