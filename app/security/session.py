"""Xác thực phiên theo cổng và kiểm tra vai trò dành cho các route."""

from collections.abc import Awaitable, Callable, Set

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.error.exceptions import SessionAccessError
from app.modules.identity.facade import AuthenticatedSession, Role, SessionPortal, authenticate_session
from app.security.origin import has_allowed_origin, origin_rejected

STOREFRONT_SESSION_COOKIE = "storefront_session"
PORTAL_SESSION_COOKIE = "portal_session"


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, *, api_prefix: str, origin_protected_paths: Set[str] = frozenset()
    ) -> None:
        super().__init__(app)
        self.portal_prefix = f"{api_prefix}/identity/portal"
        self.origin_protected_paths = origin_protected_paths

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        root_path = request.scope.get("root_path", "").rstrip("/")
        if root_path and (path == root_path or path.startswith(f"{root_path}/")):
            path = path[len(root_path) :] or "/"

        # Reject before authenticating or renewing a session and before dispatching to a route.
        if (
            request.method == "POST"
            and path.rstrip("/") in self.origin_protected_paths
            and not has_allowed_origin(request)
        ):
            return origin_rejected()

        if path == self.portal_prefix or path.startswith(f"{self.portal_prefix}/"):
            cookie_name, portal = PORTAL_SESSION_COOKIE, SessionPortal.PORTAL
        else:
            cookie_name, portal = STOREFRONT_SESSION_COOKIE, SessionPortal.STOREFRONT

        token = request.cookies.get(cookie_name)
        request.state.auth_portal = portal
        request.state.auth_session = (
            await authenticate_session(request, token, portal) if token else None
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
