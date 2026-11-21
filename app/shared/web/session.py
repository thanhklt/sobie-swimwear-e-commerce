"""Xác thực phiên theo cổng và kiểm tra vai trò dành cho các route."""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.modules.identity import service
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.shared.web.response import error_response

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
        request.state.auth_session = (
            await service.authenticate_session(token, portal) if token else None
        )
        return await call_next(request)


class SessionAccessError(Exception):
    def __init__(self, *, status_code: int, login_route: str | None = None):
        super().__init__(status_code)
        self.status_code = status_code
        self.login_route = login_route


async def session_access_error(request: Request, exc: SessionAccessError) -> Response:
    if exc.login_route is not None:
        return RedirectResponse(request.url_for(exc.login_route).path, status_code=303)

    if exc.status_code == 401:
        code, message = "AUTHENTICATION_REQUIRED", "Bạn cần đăng nhập."
    else:
        code, message = "FORBIDDEN", "Bạn không có quyền thực hiện thao tác này."
    return error_response(
        request, status_code=exc.status_code, code=code, message=message
    )


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
