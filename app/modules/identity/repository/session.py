"""Truy cập dữ liệu phiên đăng nhập."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import case, delete, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import IdentityAccount, IdentityRole, IdentitySession
from ..schemas import AuthenticatedSession, Role


class SessionRepository:
    async def delete_portal_session(self, db: AsyncSession, token_hash: str, roles: tuple[Role, ...]) -> None:
        accounts = select(IdentityAccount.account_key).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        ).where(IdentityRole.role_code.in_(roles))
        await db.exec(delete(IdentitySession).where(
            IdentitySession.session_token_hash == token_hash,
            IdentitySession.session_account_key.in_(accounts),
        ))

    async def session_exists(self, db: AsyncSession, session: AuthenticatedSession, now: datetime) -> bool:
        query = select(IdentitySession.session_key).where(
            IdentitySession.session_key == session.session_key,
            IdentitySession.session_account_key == session.account_key,
            IdentitySession.session_expires_at > now,
        )
        return (await db.exec(query)).first() is not None

    async def delete_account_sessions(self, db: AsyncSession, key: UUID) -> None:
        await db.exec(delete(IdentitySession).where(IdentitySession.session_account_key == key))

    async def insert_session(self, db: AsyncSession, *, account_key: UUID, token_hash: str,
                             created_at: datetime, expires_at: datetime) -> None:
        db.add(IdentitySession(session_account_key=account_key, session_token_hash=token_hash,
                               session_created_at=created_at, session_last_seen_at=created_at,
                               session_expires_at=expires_at))
        await db.flush()

    async def renew_session(self, db: AsyncSession, *, token_hash: str,
                            allowed_roles: tuple[Role, ...], seen_at: datetime,
                            expires_at: datetime) -> AuthenticatedSession | None:
        eligible = select(IdentityAccount.account_key).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        ).where(IdentityAccount.account_status == "ACTIVE",
                IdentityRole.role_code.in_([role.value for role in allowed_roles]))
        role_query = select(IdentityRole.role_code).join(
            IdentityAccount, IdentityAccount.account_role_key == IdentityRole.role_key
        ).where(IdentityAccount.account_key == IdentitySession.session_account_key).scalar_subquery()
        statement = update(IdentitySession).where(
            IdentitySession.session_token_hash == token_hash,
            IdentitySession.session_expires_at > seen_at,
            IdentitySession.session_account_key.in_(eligible),
        ).values(
            session_last_seen_at=case((IdentitySession.session_last_seen_at < seen_at, seen_at),
                                      else_=IdentitySession.session_last_seen_at),
            session_expires_at=case((IdentitySession.session_last_seen_at < seen_at, expires_at),
                                    else_=IdentitySession.session_expires_at),
        ).returning(IdentitySession.session_key, IdentitySession.session_account_key, role_query)
        row = (await db.exec(statement)).one_or_none()
        return AuthenticatedSession(row[0], row[1], Role(row[2])) if row else None
