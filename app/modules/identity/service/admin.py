"""Danh sách, tạo, sửa và khóa tài khoản trong portal."""

from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from app.database.transaction import transaction
from app.error.exceptions import SessionAccessError
from app.modules.shopping.service import initialize_customer_shopping

from ..models import IdentityAccount
from ..repository import AccountRepository, SessionRepository
from ..schemas import AccountFormError, AuthenticatedSession, Role
from . import _rules
from .account import active_actor, check_contacts, map_account_integrity_error, public_account


class AdminAccountService:
    def __init__(self, accounts: AccountRepository, sessions: SessionRepository, session_factory):
        self.accounts = accounts
        self.sessions = sessions
        self.session_factory = session_factory

    async def search_accounts(self, *, customers_only: bool, search: str, page: int):
        size = 20
        async with self.session_factory() as db:
            rows = await self.accounts.list_accounts(
                db, customers=customers_only, search=search, offset=(page - 1) * size, limit=size + 1
            )
            return [public_account(account, Role(role)) for account, role in rows[:size]], len(rows) > size

    async def create_managed_account(self, actor: AuthenticatedSession, fields: dict[str, str], password: str) -> None:
        role = self._submitted_role(fields.get("role", ""))
        values = _rules.validate_profile(fields, role, creating=True)
        if message := _rules.password_validation_error(password, password):
            raise AccountFormError("password", message)
        try:
            async with self.session_factory() as db, transaction(db):
                await self.accounts.role_key(db, Role.ADMIN, lock=True)
                await active_actor(self.accounts, self.sessions, db, actor, (Role.ADMIN,))
                await check_contacts(self.accounts, db, values)
                now = _rules.utc_now()
                account = IdentityAccount(
                    **values,
                    account_role_key=await self.accounts.role_key(db, role),
                    account_id=await self._allocate_account_code(db, role, values, now),
                    account_hash_password=await self.accounts.hash_password(db, password=password),
                    account_created_at=now,
                )
                key = await self.accounts.save_account(db, account)
                if role == Role.CUSTOMER:
                    await initialize_customer_shopping(db, account_key=key)
        except IntegrityError as exc:
            map_account_integrity_error(exc)

    async def edit_managed_account(self, actor: AuthenticatedSession, key: UUID, fields: dict[str, str]) -> bool:
        try:
            async with self.session_factory() as db, transaction(db):
                admin_key = await self.accounts.role_key(db, Role.ADMIN, lock=True)
                await active_actor(self.accounts, self.sessions, db, actor, (Role.ADMIN,))
                record = await self.accounts.account_record(db, key, lock=True)
                if record is None:
                    raise AccountFormError("", "Không tìm thấy tài khoản")
                account, previous_role = record
                role = self._submitted_role(fields["role"]) if "role" in fields else previous_role
                changed_role = previous_role != role
                if changed_role and Role.CUSTOMER in (role, previous_role):
                    raise AccountFormError("role", "Không thể chuyển giữa Khách hàng và vai trò nội bộ")
                if changed_role and previous_role == Role.ADMIN and account.account_status == "ACTIVE":
                    await self._require_remaining_admin(db, admin_key, key)

                # Trường bị bỏ qua giữ giá trị hiện tại, kể cả khi chỉ gửi vai trò mới.
                values = _rules.validate_profile(_rules.profile_values(account) | fields, role)
                updates = {column: value for column, value in values.items()
                           if column.removeprefix("account_") in fields}
                await check_contacts(self.accounts, db, updates, key)
                account.sqlmodel_update(updates)
                if changed_role:
                    account.account_id = await self._allocate_account_code(db, role, values, _rules.utc_now())
                    account.account_role_key = await self.accounts.role_key(db, role)
                    await self.sessions.delete_account_sessions(db, key)
                await self.accounts.save_account(db, account)
                return changed_role
        except IntegrityError as exc:
            map_account_integrity_error(exc)

    async def set_account_lock(self, actor: AuthenticatedSession, key: UUID, *, locked: bool) -> None:
        async with self.session_factory() as db, transaction(db):
            admin_key = await self.accounts.role_key(db, Role.ADMIN, lock=True)
            roles = (Role.ADMIN, Role.EMPLOYEE) if locked else (Role.ADMIN,)
            _, actor_role = await active_actor(self.accounts, self.sessions, db, actor, roles)
            record = await self.accounts.account_record(db, key, lock=True)
            if not record or (actor_role == Role.EMPLOYEE and record[1] != Role.CUSTOMER):
                raise SessionAccessError(status_code=403)
            account, role = record
            if locked and role == Role.ADMIN and account.account_status == "ACTIVE":
                await self._require_remaining_admin(db, admin_key, key)
            account.account_status = "LOCKED" if locked else "ACTIVE"
            await self.accounts.save_account(db, account)
            if locked:
                await self.sessions.delete_account_sessions(db, key)

    async def _allocate_account_code(self, db, role: Role, values: dict, now) -> str:
        prefix = _rules.account_code_prefix(role)
        if role == Role.CUSTOMER:
            date_part = now.astimezone(ZoneInfo(_rules.VIETNAM_TIMEZONE)).strftime("%Y%m%d")
            body = date_part
        else:
            name = _rules.internal_code_name(values["account_name"])
            birth = values["account_date_of_birth"].strftime("%Y%m%d")
            if not 1 <= len(name) <= 83:
                raise AccountFormError("name", "Họ tên không hợp lệ để cấp mã tài khoản nội bộ")
            body = f"{name}-{birth}"
        suffix = await self.accounts.next_account_suffix(db, prefix=prefix)
        return f"{prefix}-{body}-{suffix}"

    @staticmethod
    def _submitted_role(value: str) -> Role:
        try:
            return Role(value)
        except ValueError as exc:
            raise AccountFormError("role", "Vai trò không hợp lệ") from exc

    async def _require_remaining_admin(self, db, admin_key: UUID, target: UUID) -> None:
        if not await self.accounts.another_active_admin(db, admin_key, target):
            raise AccountFormError("", "Hệ thống phải còn ít nhất một Admin đang hoạt động")
