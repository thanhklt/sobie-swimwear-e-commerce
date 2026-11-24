"""Xác thực phiên theo cổng và kiểm tra vai trò dành cho các route."""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.error.exceptions import SessionAccessError
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal

PORTAL_PREFIX = "/admin"
STOREFRONT_SESSION_COOKIE = "storefront_session"
PORTAL_SESSION_COOKIE = "portal_session"


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        root_path = request.scope.get("root_path", "").rstrip("/")
        if root_path and (path == root_path or path.startswith(f"{root_path}/")):
            path = path[len(root_path) :] or "/"

        if path == PORTAL_PREFIX or path.startswith(f"{PORTAL_PREFIX}/"):
            cookie_name, portal = PORTAL_SESSION_COOKIE, SessionPortal.PORTAL
        else:
            cookie_name, portal = STOREFRONT_SESSION_COOKIE, SessionPortal.STOREFRONT

        token = request.cookies.get(cookie_name)
        request.state.auth_portal = portal
        request.state.auth_session = (
            await request.app.state.identity_service.authenticate_session(token, portal) if token else None
        )
        return await call_next(request)


def require_roles(
    *roles: Role, login_route: str | None = None
) -> Callable[[Request], Awaitable[AuthenticatedSession]]:
    """Tạo dependency cấp quyền cho đúng các vai trò route khai báo."""
    if not roles:
        raise ValueError("Cần ít nhất một vai trò.")

    async def check_role(request: Request) -> AuthenticatedSession:
        session = getattr(request.state, "auth_session", None)
        if session is None:
            raise SessionAccessError(status_code=401, login_route=login_route)
        if session.role not in roles:
            raise SessionAccessError(status_code=403)
        return session

    return check_role
