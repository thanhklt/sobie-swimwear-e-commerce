"""Cửa công khai để xác thực phiên của module identity."""

from starlette.requests import Request

from .schemas import AuthenticatedSession, Role, SessionPortal

__all__ = ("AuthenticatedSession", "Role", "SessionPortal", "authenticate_session")


async def authenticate_session(
    request: Request, token: str, portal: SessionPortal
) -> AuthenticatedSession | None:
    return await request.app.state.identity.sessions.authenticate_session(token, portal)
