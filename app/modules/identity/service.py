"""Tầng Service của module identity: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Lấy tài khoản và vai trò từ mã phiên trong cookie, gia hạn phiên (kiểm tra quyền mỗi request).
- Lấy thông tin nhận hàng mặc định của Khách hàng (cho ordering).
- Kiểm tra tài khoản có vai trò Khách hàng (cho shopping).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from datetime import UTC, datetime, timedelta
from hashlib import sha256

from app.modules.identity import repository
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.shared.database.transaction import transaction

_SESSION_POLICIES = {
    SessionPortal.STOREFRONT: ((Role.CUSTOMER,), timedelta(minutes=30)),
    SessionPortal.PORTAL: ((Role.EMPLOYEE, Role.ADMIN), timedelta(hours=1)),
}


async def authenticate_session(
    token: str, portal: SessionPortal
) -> AuthenticatedSession | None:
    """Xác thực cookie phía server và gia hạn phiên còn hiệu lực."""
    if not token:
        return None

    from app.shared.database.engine import session_factory

    allowed_roles, lifetime = _SESSION_POLICIES[portal]
    seen_at = datetime.now(UTC)
    token_hash = sha256(token.encode("utf-8")).hexdigest()

    async with session_factory() as db, transaction(db):
        return await repository.renew_session(
            db,
            token_hash=token_hash,
            allowed_roles=allowed_roles,
            seen_at=seen_at,
            expires_at=seen_at + lifetime,
        )


async def account_email(db, account_key):
    """Lấy email người mua để chụp vào hóa đơn từ module ordering."""
    return await repository.account_email(db, account_key)
