"""Tầng Repository của module identity: truy vấn các bảng do module sở hữu:
- identity.role
- identity.account
- identity.session

Không truy vấn bảng của module khác.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, bindparam, text

from app.modules.identity.session import AuthenticatedSession, Role

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


_RENEW_SESSION = text(
    """
    WITH eligible_session AS (
        SELECT account.account_key, role.role_code
        FROM identity.session AS candidate
        JOIN identity.account AS account ON account.account_key = candidate.session_account_key
        JOIN identity.role AS role ON role.role_key = account.account_role_key
        WHERE candidate.session_token_hash = :token_hash
          AND account.account_status = 'ACTIVE'
          AND role.role_code IN :allowed_roles
    )
    UPDATE identity.session
    SET session_last_seen_at = CASE
            WHEN session_last_seen_at < :seen_at THEN :seen_at
            ELSE session_last_seen_at
        END,
        session_expires_at = CASE
            WHEN session_last_seen_at < :seen_at THEN :expires_at
            ELSE session_expires_at
        END
    WHERE session_token_hash = :token_hash
      AND session_expires_at > :seen_at
      AND session_account_key IN (SELECT account_key FROM eligible_session)
    RETURNING session_key, session_account_key,
        (SELECT role_code FROM eligible_session) AS role_code
    """
).bindparams(
    bindparam("allowed_roles", expanding=True),
    bindparam("seen_at", type_=DateTime(timezone=True)),
    bindparam("expires_at", type_=DateTime(timezone=True)),
)


async def renew_session(
    db: AsyncSession,
    *,
    token_hash: str,
    allowed_roles: tuple[Role, ...],
    seen_at: datetime,
    expires_at: datetime,
) -> AuthenticatedSession | None:
    """Gia hạn nguyên tử phiên còn hạn thuộc tài khoản và cổng hợp lệ."""
    result = await db.exec(
        _RENEW_SESSION,
        params={
            "token_hash": token_hash,
            "allowed_roles": tuple(role.value for role in allowed_roles),
            "seen_at": seen_at,
            "expires_at": expires_at,
        },
    )
    row = result.mappings().one_or_none()
    if row is None:
        return None

    return AuthenticatedSession(
        session_key=UUID(str(row["session_key"])),
        account_key=UUID(str(row["session_account_key"])),
        role=Role(row["role_code"]),
    )


async def account_email(db, account_key: UUID) -> str | None:
    result = await db.exec(
        text("SELECT account_email FROM identity.account WHERE account_key = :account_key"),
        params={"account_key": account_key},
    )
    row = result.first()
    return row[0] if row else None
