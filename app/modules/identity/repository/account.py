"""Truy cập dữ liệu tài khoản."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models import IdentityAccount, IdentityRole
from ..schemas import Account, Role


class AccountRepository:
    async def find_account(self, db: AsyncSession, *, email: str | None = None,
                           google_sub: str | None = None, account_key: UUID | None = None,
                           phone: str | None = None,
                           for_update: bool = False) -> Account | None:
        query = select(IdentityAccount, IdentityRole.role_code).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        )
        if email is not None:
            query = query.where(func.lower(IdentityAccount.account_email) == email.lower())
        elif phone is not None:
            query = query.where(IdentityAccount.account_phone_number == phone)
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
                       Role(role), account.account_status, account.account_hash_password)

    async def verify_password(self, db: AsyncSession, password: str, password_hash: str | None) -> bool:
        if password_hash is None or len(password.encode('utf-8')) > 72 or '\x00' in password:
            return False
        return (await db.exec(select(func.crypt(password, password_hash) == password_hash))).one()

    async def account_record(self, db: AsyncSession, key: UUID, *, lock: bool = False):
        query = select(IdentityAccount, IdentityRole.role_code).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        ).where(IdentityAccount.account_key == key)
        if lock:
            query = query.with_for_update(of=IdentityAccount)
        row = (await db.exec(query)).one_or_none()
        return (row[0], Role(row[1])) if row else None

    async def list_accounts(self, db: AsyncSession, *, customers: bool, search: str, offset: int, limit: int):
        query = select(IdentityAccount, IdentityRole.role_code).join(
            IdentityRole, IdentityRole.role_key == IdentityAccount.account_role_key
        )
        if customers:
            query = query.where(IdentityRole.role_code == Role.CUSTOMER)
        if search:
            query = query.where(or_(
                IdentityAccount.account_name.icontains(search, autoescape=True),
                IdentityAccount.account_email.icontains(search, autoescape=True),
                IdentityAccount.account_phone_number.icontains(search, autoescape=True),
            ))
        return (await db.exec(query.order_by(IdentityAccount.account_id).offset(offset).limit(limit))).all()

    async def role_key(self, db: AsyncSession, role: Role, *, lock: bool = False) -> UUID:
        query = select(IdentityRole.role_key).where(IdentityRole.role_code == role)
        if lock:
            query = query.with_for_update()
        return (await db.exec(query)).one()

    async def another_active_admin(self, db: AsyncSession, role_key: UUID, target: UUID) -> bool:
        query = select(IdentityAccount.account_key).where(
            IdentityAccount.account_role_key == role_key,
            IdentityAccount.account_status == "ACTIVE",
            IdentityAccount.account_key != target,
        ).limit(1)
        return (await db.exec(query)).first() is not None

    async def save_account(self, db: AsyncSession, account: IdentityAccount) -> UUID:
        db.add(account)
        await db.flush()
        return account.account_key

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
