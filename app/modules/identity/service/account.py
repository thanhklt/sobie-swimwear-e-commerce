"""Hồ sơ và mật khẩu của tài khoản hiện tại."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.database.transaction import transaction
from app.error.exceptions import SessionAccessError

from ..repository import AccountRepository, SessionRepository
from ..schemas import AccountFormError, AuthenticatedSession, Role, SessionPortal
from . import _rules
from ._otp_flow import _EMAIL_IN_USE


class AccountService:
    def __init__(self, accounts: AccountRepository, sessions: SessionRepository, session_factory):
        self.accounts = accounts
        self.sessions = sessions
        self.session_factory = session_factory

    async def get_account_details(self, key: UUID, *, customers_only: bool = False):
        async with self.session_factory() as db:
            record = await self.accounts.account_record(db, key)
            if not record or (customers_only and record[1] != Role.CUSTOMER):
                return None
            return public_account(*record)

    # UC-04 Main 3–5, E1, E2, AC-2 — Lưu hồ sơ storefront, giữ email của tài khoản.
    async def update_profile(self, actor: AuthenticatedSession, fields: dict[str, str]) -> None:
        values = _rules.validate_profile(fields, Role.CUSTOMER, include_email=False)
        try:
            async with self.session_factory() as db, transaction(db):
                account, _ = await active_actor(self.accounts, self.sessions, db, actor, (Role.CUSTOMER,))
                await check_contacts(self.accounts, db, values, actor.account_key)
                account.sqlmodel_update(values)
                await self.accounts.save_account(db, account)
        except IntegrityError as exc:
            map_account_integrity_error(exc)

    async def change_password(
        self, actor: AuthenticatedSession, portal: SessionPortal, current: str, password: str, confirmation: str
    ) -> None:
        roles, _ = _rules.SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            account, _ = await active_actor(self.accounts, self.sessions, db, actor, roles)
            if not await self.accounts.verify_password(db, current, account.account_hash_password):
                raise AccountFormError("current_password", "Mật khẩu hiện tại không đúng")
            if message := _rules.password_validation_error(password, password):
                raise AccountFormError("password", message)
            if password == current:
                raise AccountFormError("password", "Mật khẩu mới phải khác mật khẩu hiện tại")
            if password != confirmation:
                raise AccountFormError("password_confirmation", "Mật khẩu nhập lại không khớp")
            account.account_hash_password = await self.accounts.hash_password(db, password=password)
            await self.accounts.save_account(db, account)
            await self.sessions.delete_account_sessions(db, actor.account_key)


async def active_actor(accounts: AccountRepository, sessions: SessionRepository, db, actor: AuthenticatedSession, roles: tuple[Role, ...]):
    record = await accounts.account_record(db, actor.account_key, lock=True)
    if not record or record[1] not in roles or record[0].account_status != "ACTIVE":
        raise SessionAccessError(status_code=403)
    if not await sessions.session_exists(db, actor, _rules.utc_now()):
        raise SessionAccessError(status_code=403)
    return record


def public_account(account, role: Role) -> dict:
    return _rules.profile_values(account) | {
        "key": account.account_key, "code": account.account_id,
        "role": role, "status": account.account_status,
        "has_password": account.account_hash_password is not None,
    }


async def check_contacts(accounts: AccountRepository, db, fields: dict, key: UUID | None = None) -> None:
    for field, lookup in (("email", "email"), ("phone_number", "phone")):
        value = fields.get(f"account_{field}")
        if value:
            existing = await accounts.find_account(db, **{lookup: value})
            if existing and existing.account_key != key:
                raise AccountFormError(field, _contact_conflict(field))


def _contact_conflict(field: str) -> str:
    return _EMAIL_IN_USE if field == "email" else "Số điện thoại đã được sử dụng"


def map_account_integrity_error(exc: IntegrityError) -> None:
    constraint = getattr(getattr(exc.orig, "__cause__", None), "constraint_name", "") or ""
    for field in ("email", "phone_number"):
        if f"account_{field}_" in constraint:
            raise AccountFormError(field, _contact_conflict(field)) from exc
    raise exc
