"""Endpoint đăng nhập và đăng xuất cho storefront và portal."""

import logging
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, Response
from redis.exceptions import RedisError

from app.shared.web.rendering import templates

from ..schemas import RegistrationResult, SessionPortal
from ._web import (
    _COOKIE_FLAGS,
    _ORIGIN_FORM_HEADERS,
    _SESSION_COOKIES,
    _browser_cookie,
    _checkout_requested,
    _home,
    _redirect,
    _set_session_cookie,
    _storefront_destination,
    RegistrationServiceDep,
    SessionServiceDep,
)

router = APIRouter()
logger = logging.getLogger(__package__)


@router.get("/login", response_class=HTMLResponse, name="storefront_login")
# UC-01 Đăng ký tài khoản — Main 8; 1b.5 (specs/use-cases/identity/UC-01-register-account.md)
async def storefront_login_form(request: Request, registration: RegistrationServiceDep) -> Response:
    if request.state.auth_session is not None:
        return _redirect(_storefront_destination(request, _checkout_requested(request)))

    browser = _browser_cookie(request)
    registered = False
    if browser:
        try:
            registered = await registration.consume_registration_success(browser)
        except Exception as exc:
            logger.warning("Registration success notice unavailable (%s)", type(exc).__name__)
    return _login_page(request, registered=registered)


def _login_page(request: Request, *, registered: bool = False, result: RegistrationResult | None = None,
                identifier: str = "") -> Response:
    result = result or RegistrationResult()
    portal = request.state.auth_portal == SessionPortal.PORTAL
    template = "identity/auth/portal_login.html" if portal else "identity/auth/login.html"
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
    sessions: SessionServiceDep,
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
        result = await sessions.login_with_password(
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
@router.post("/portal/logout", name="portal_logout")
async def logout(request: Request, sessions: SessionServiceDep) -> Response:
    portal = request.state.auth_portal
    name = _SESSION_COOKIES[portal]
    await sessions.logout(request.cookies.get(name), portal)
    response = _home(request)
    response.delete_cookie(name, **_COOKIE_FLAGS)
    return response
