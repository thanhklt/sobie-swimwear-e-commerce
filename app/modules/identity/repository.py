"""Truy cập dữ liệu thuộc module identity."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.identity.models import IdentityAccount, IdentityRole, IdentitySession
from app.modules.identity.session import AuthenticatedSession, Role


@dataclass(frozen=True, slots=True)
class Account:
    account_key: UUID
    email: str
    google_sub: str | None
    role: Role
    status: str


class IdentityRepository:
    async def find_account(self, db: AsyncSession, *, email: str | None = None,
                           google_sub: str | None = None, account_key: UUID | None = None,
                           for_update: bool = False) -> Account | None:
        query = select(IdentityAccount, IdentityRole.role_code).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        )
        if email is not None:
            query = query.where(func.lower(IdentityAccount.account_email) == email.lower())
        elif google_sub is not None:
            query = query.where(IdentityAccount.account_google_sub == google_sub)
        elif account_key is not None:
            query = query.where(IdentityAccount.account_key == account_key)
        else:
            raise ValueError("Account lookup requires an identifier")
        if for_update or account_key is not None:
            query = query.with_for_update(of=IdentityAccount)
        row = (await db.exec(query)).one_or_none()
        if row is None:
            return None
        account, role = row
        return Account(account.account_key, account.account_email, account.account_google_sub,
                       Role(role), account.account_status)

    async def next_account_suffix(self, db: AsyncSession, *, prefix: str) -> str:
        result = await db.exec(select(func.identity.next_account_suffix(prefix)))
        return result.one()

    async def hash_password(self, db: AsyncSession, *, password: str) -> str:
        result = await db.exec(select(func.crypt(password, func.gen_salt("bf", 10))))
        return result.one()

    async def insert_customer(self, db: AsyncSession, *, account_id: str, email: str,
                              password_hash: str | None, google_sub: str | None,
                              created_at: datetime) -> UUID:
        role = (await db.exec(select(IdentityRole.role_key).where(
            IdentityRole.role_code == "customer"))).one()
        account = IdentityAccount(account_id=account_id, account_role_key=role,
                                  account_email=email, account_hash_password=password_hash,
                                  account_google_sub=google_sub, account_created_at=created_at)
        db.add(account)
        await db.flush()
        return account.account_key

    async def link_google_account(self, db: AsyncSession, *, account_key: UUID, google_sub: str) -> None:
        await db.exec(update(IdentityAccount).where(
            IdentityAccount.account_key == account_key
        ).values(account_google_sub=google_sub))

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
