"""Tầng Service của module identity: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Lấy tài khoản và vai trò từ mã phiên trong cookie, gia hạn phiên (kiểm tra quyền mỗi request).
- Lấy thông tin nhận hàng mặc định của Khách hàng (cho ordering).
- Kiểm tra tài khoản có vai trò Khách hàng (cho shopping).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

import json
import logging
from dataclasses import asdict, dataclass, replace
from datetime import timedelta
from hashlib import sha256
from hmac import compare_digest, digest
from math import ceil
from secrets import token_urlsafe
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from app.config.settings import Config
from app.database.transaction import transaction
from app.error.exceptions import SessionAccessError
from app.modules.identity.account_details import (
    AccountFormError, account_code_prefix, internal_code_name, profile_values, validate_profile,
)
from app.modules.identity.models import IdentityAccount
from app.modules.identity import helper, repository
from app.modules.identity.google_oidc import GoogleIdentity, get_google_oidc
from app.modules.identity.mail import send_registration_otp
from app.modules.identity.registration_challenges import ChallengeStore, get_challenge_store
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.modules.shopping.service import initialize_customer_shopping

_SESSION_POLICIES = {
    SessionPortal.STOREFRONT: ((Role.CUSTOMER,), timedelta(minutes=30)),
    SessionPortal.PORTAL: ((Role.EMPLOYEE, Role.ADMIN), timedelta(hours=1)),
}


_OTP_SECONDS = 300
_OTP_TRIES = 5
_OTP_LOCK_SECONDS = 300
_OTP_FLOW_SECONDS = 1800
_GRANT_SECONDS = 600
_GOOGLE_SECONDS = 600
_BUSY_SECONDS = 300
_FLASH_SECONDS = 120
_EMAIL_IN_USE = "Email đã được sử dụng"
_OTP_INVALID = "Mã xác minh không đúng hoặc đã hết hạn."
_RESEND_EARLY = "Bạn có thể gửi lại mã sau 5 phút kể từ lần gửi gần nhất."
_REGISTRATION_FAILED = "Đăng ký không thành công. Vui lòng thử lại."
_GOOGLE_FAILED = "Không thể xác thực Google. Vui lòng thử lại."
_GOOGLE_ACCOUNT_MISSING = "Email Google này chưa có tài khoản Sobie. Hãy chọn Đăng ký với Google."
_RESTART = "Lượt xác minh đã hết hạn. Vui lòng bắt đầu lại."

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    stage: str = "email"
    message: str = ""
    email: str = ""
    field: str = ""
    status: int = 200
    location: str = ""
    session_token: str = ""
    otp_locked: bool = False
    checkout: bool = False


@dataclass(frozen=True, slots=True)
class _Flow:
    kind: str
    stamp: str
    retain_until: float
    email: str = ""
    expires_at: float = 0
    otp_digest: str = ""
    attempts: int = 0
    account_key: str = ""
    google_sub: str = ""
    nonce: str = ""
    verifier: str = ""
    allow_create: bool = True
    retry_at: float = 0
    checkout: bool = False

    def encode(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))

    @classmethod
    def new(cls, kind: str, seconds: int, **kwargs) -> "_Flow":
        return cls(kind, token_urlsafe(32), helper.utc_timestamp() + seconds, **kwargs)


class _GoogleRejected(Exception):
    """Kết quả xác thực không đáp ứng điều kiện của storefront."""


def _flow_key(browser: str) -> str:
    return "identity:registration:flow:" + sha256(browser.encode("ascii")).hexdigest()


def _google_flow_key(browser: str, state: str) -> str:
    value = sha256(f"{browser}:{state}".encode("utf-8")).hexdigest()
    return f"identity:registration:google:{value}"


def _cooldown_key(purpose: str, email: str) -> str:
    return f"identity:registration:cooldown:{purpose}:" + sha256(
        email.lower().encode("utf-8")
    ).hexdigest()


def _otp_digest(flow: _Flow, otp: str) -> str:
    return digest(
        Config.SECRET_KEY.encode("utf-8"),
        f"{flow.kind}:{flow.stamp}:{flow.email}:{otp}".encode("utf-8"),
        "sha256",
    ).hex()


async def _read_flow(store: ChallengeStore, key: str) -> tuple[str | None, _Flow | None]:
    raw = await store.get(key)
    if raw is None:
        return None, None
    flow = _Flow(**json.loads(raw))
    return raw, flow if flow.retain_until > helper.utc_timestamp() else None


async def _write_flow(
    store: ChallengeStore, key: str, expected: str | None, flow: _Flow | None
) -> bool:
    if flow is None:
        return await store.compare_and_set(key, expected, None)
    ttl = ceil(flow.retain_until - helper.utc_timestamp())
    if ttl <= 0:
        return False
    return await store.compare_and_set(key, expected, flow.encode(), ttl)


def _flow_problem(
    stage: str = "email", message: str = _RESTART, *, email: str = "", status: int = 400
) -> RegistrationResult:
    return RegistrationResult(stage, message, email, status=status)


def _locked_otp(flow: _Flow) -> RegistrationResult:
    if helper.utc_timestamp() < flow.retry_at:
        message = "Bạn đã nhập sai mã 5 lần. Hãy chờ đủ 5 phút kể từ lần sai cuối rồi yêu cầu mã mới."
    else:
        message = "Mã này đã bị khóa sau 5 lần nhập sai. Hãy yêu cầu mã mới."
    return RegistrationResult(flow.kind, message, flow.email, status=429, otp_locked=True, checkout=flow.checkout)


async def _send_challenge(
    store: ChallengeStore,
    key: str,
    expected: str | None,
    flow: _Flow,
    *,
    previous: _Flow | None = None,
) -> RegistrationResult:
    stage = flow.kind
    cooldown = _cooldown_key(stage, flow.email)
    pending = _Flow.new("busy", _BUSY_SECONDS)
    if not await _write_flow(store, key, expected, pending):
        return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)

    claim = token_urlsafe(32)
    if not await store.compare_and_set(cooldown, None, claim, _BUSY_SECONDS):
        await _write_flow(store, key, pending.encode(), previous)
        if previous and previous.attempts <= 0:
            return _locked_otp(previous)
        return _flow_problem(stage if previous else "email", _RESEND_EARLY, email=flow.email)

    otp = helper.generate_otp()
    while previous and compare_digest(_otp_digest(previous, otp), previous.otp_digest):
        otp = helper.generate_otp()

    try:
        await send_registration_otp(flow.email, otp)
    except Exception as exc:
        logger.warning("Registration OTP delivery failed (%s)", type(exc).__name__)
        await store.compare_and_set(cooldown, claim, None)
        await _write_flow(store, key, pending.encode(), previous)
        problem = _flow_problem(
            stage if previous else "email",
            "Không thể gửi mã xác minh. Vui lòng thử lại.",
            email=flow.email,
            status=503,
        )
        return replace(problem, otp_locked=True) if previous and previous.attempts <= 0 else problem

    sent_at = helper.utc_timestamp()
    challenge = replace(
        flow,
        otp_digest=_otp_digest(flow, otp),
        attempts=_OTP_TRIES,
        expires_at=sent_at + _OTP_SECONDS,
        retain_until=sent_at + (_OTP_FLOW_SECONDS if stage == "otp" else _OTP_SECONDS),
    )
    # The cooldown is counted from successful SMTP delivery, including across browsers.
    if not await store.compare_and_set(cooldown, claim, claim, _OTP_SECONDS):
        raise RuntimeError("The OTP delivery reservation expired")
    if not await _write_flow(store, key, pending.encode(), challenge):
        raise RuntimeError("The registration challenge expired during delivery")
    return RegistrationResult(stage, "Đã gửi mã xác minh.", flow.email)


async def _verify_otp(
    store: ChallengeStore, key: str, kind: str, otp: str, *, next_kind: str, next_seconds: int
) -> tuple[_Flow | None, RegistrationResult | None]:
    raw, flow = await _read_flow(store, key)
    if raw is None or flow is None or flow.kind != kind:
        return None, _flow_problem()
    stamp = flow.stamp
    invalid = _flow_problem(kind, _OTP_INVALID, email=flow.email)
    matches = len(otp) == 6 and otp.isascii() and otp.isdigit() and compare_digest(
        _otp_digest(flow, otp), flow.otp_digest
    )
    while raw is not None and flow is not None and flow.kind == kind and flow.stamp == stamp:
        now = helper.utc_timestamp()
        if flow.attempts <= 0:
            return None, _locked_otp(flow)
        if now >= flow.expires_at:
            break

        if matches:
            following = _Flow.new(
                next_kind, next_seconds, email=flow.email,
                account_key=flow.account_key, google_sub=flow.google_sub, checkout=flow.checkout,
            )
            if await _write_flow(store, key, raw, following):
                return following, None
        elif flow.attempts == 1:
            retry_at = now + _OTP_LOCK_SECONDS
            locked = replace(flow, attempts=0, retry_at=retry_at,
                             retain_until=max(flow.retain_until, retry_at + _OTP_SECONDS))
            if await store.exhaust_otp(
                key, raw, locked.encode(), ceil(locked.retain_until - now),
                cooldown_key=_cooldown_key(kind, flow.email), cooldown_seconds=_OTP_LOCK_SECONDS,
            ):
                return None, _locked_otp(locked)
        elif await _write_flow(store, key, raw, replace(flow, attempts=flow.attempts - 1)):
            return None, invalid

        # A concurrent update may have charged another attempt. Retry only against the same OTP.
        raw, flow = await _read_flow(store, key)
    return None, invalid


def _check_customer(account: repository.Account) -> None:
    if account.role != Role.CUSTOMER:
        raise _GoogleRejected("Thông tin đăng nhập không đúng")
    if account.status != "ACTIVE":
        raise _GoogleRejected("Tài khoản đã bị khóa")


def _google_conflict(exc: IntegrityError) -> bool:
    # asyncpg wraps the PostgreSQL constraint error in its DBAPI adapter.
    constraint = getattr(getattr(exc.orig, "__cause__", None), "constraint_name", None)
    return constraint in {"account_account_email_key", "account_account_google_sub_key"}


class IdentityService:
    """Điều phối nghiệp vụ identity."""

    def __init__(self, repository, session_factory):
        self.repository = repository
        self.session_factory = session_factory

    async def authenticate_session(
        self,
        token: str, portal: SessionPortal
    ) -> AuthenticatedSession | None:
        """Xác thực cookie phía server và gia hạn phiên còn hiệu lực."""
        if not token:
            return None


        allowed_roles, lifetime = _SESSION_POLICIES[portal]
        seen_at = helper.utc_now()
        token_hash = sha256(token.encode("utf-8")).hexdigest()

        async with self.session_factory() as db, transaction(db):
            return await self.repository.renew_session(
                db,
                token_hash=token_hash,
                allowed_roles=allowed_roles,
                seen_at=seen_at,
                expires_at=seen_at + lifetime,
            )


    async def login_with_password(
        self, identifier: str, password: str, portal: SessionPortal, client_ip: str
    ) -> RegistrationResult:
        ip_key = sha256(client_ip.encode("utf-8")).hexdigest()
        if await get_challenge_store().count_password_attempt(ip_key) > 5:
            return RegistrationResult(message="Quá nhiều lần đăng nhập. Vui lòng thử lại sau.", status=429)
        identifier = identifier.strip()
        if not identifier or not password:
            field = "identifier" if not identifier else "password"
            return RegistrationResult(message="Vui lòng điền thông tin đăng nhập.", field=field, status=400)
        rejected = RegistrationResult(message="Thông tin đăng nhập không đúng", status=401)
        if len(identifier) > 255 or "\x00" in identifier:
            return rejected
        if "@" in identifier:
            try:
                lookup = {"email": helper.normalize_email(identifier)}
            except ValueError:
                lookup = {"email": identifier}
        else:
            lookup = {"phone": identifier}
        allowed_roles, _ = _SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            account = await self.repository.find_account(db, for_update=True, **lookup)
            if not account or not await self.repository.verify_password(db, password, account.password_hash):
                return rejected
            if account.role not in allowed_roles:
                return rejected
            if account.status != "ACTIVE":
                return RegistrationResult(message="Tài khoản đã bị khóa", status=403)
            token = await self._issue_session(db, account, portal)
            return RegistrationResult(stage="signed_in", session_token=token)

    async def logout(self, token: str | None, portal: SessionPortal) -> None:
        if not token:
            return
        roles, _ = _SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            await self.repository.delete_portal_session(db, sha256(token.encode("utf-8")).hexdigest(), roles)

    async def _active_actor(self, db, actor: AuthenticatedSession, roles: tuple[Role, ...]):
        record = await self.repository.account_record(db, actor.account_key, lock=True)
        if not record or record[1] not in roles or record[0].account_status != "ACTIVE":
            raise SessionAccessError(status_code=403)
        if not await self.repository.session_exists(db, actor, helper.utc_now()):
            raise SessionAccessError(status_code=403)
        return record

    @staticmethod
    def _public_account(account, role: Role) -> dict:
        return profile_values(account) | {
            "key": account.account_key, "code": account.account_id,
            "role": role, "status": account.account_status,
            "has_password": account.account_hash_password is not None,
        }

    async def get_account_details(self, key: UUID, *, customers_only: bool = False):
        async with self.session_factory() as db:
            record = await self.repository.account_record(db, key)
            if not record or (customers_only and record[1] != Role.CUSTOMER):
                return None
            return self._public_account(*record)

    async def search_accounts(self, *, customers_only: bool, search: str, page: int):
        size = 20
        async with self.session_factory() as db:
            rows = await self.repository.list_accounts(
                db, customers=customers_only, search=search, offset=(page - 1) * size, limit=size + 1
            )
            return [self._public_account(account, Role(role)) for account, role in rows[:size]], len(rows) > size

    async def _check_contacts(self, db, fields: dict, key: UUID | None = None) -> None:
        for field, lookup in (("email", "email"), ("phone_number", "phone")):
            value = fields.get(f"account_{field}")
            if value:
                existing = await self.repository.find_account(db, **{lookup: value})
                if existing and existing.account_key != key:
                    raise AccountFormError(field, self._contact_conflict(field))

    @staticmethod
    def _contact_conflict(field: str) -> str:
        return _EMAIL_IN_USE if field == "email" else "Số điện thoại đã được sử dụng"

    def _map_account_integrity_error(self, exc: IntegrityError) -> None:
        constraint = getattr(getattr(exc.orig, "__cause__", None), "constraint_name", "") or ""
        for field in ("email", "phone_number"):
            if f"account_{field}_" in constraint:
                raise AccountFormError(field, self._contact_conflict(field)) from exc
        raise exc

    async def update_profile(self, actor: AuthenticatedSession, fields: dict[str, str]) -> None:
        values = validate_profile(fields, Role.CUSTOMER)
        try:
            async with self.session_factory() as db, transaction(db):
                account, _ = await self._active_actor(db, actor, (Role.CUSTOMER,))
                await self._check_contacts(db, values, actor.account_key)
                account.sqlmodel_update(values)
                await self.repository.save_account(db, account)
        except IntegrityError as exc:
            self._map_account_integrity_error(exc)

    async def change_password(
        self, actor: AuthenticatedSession, portal: SessionPortal, current: str, password: str, confirmation: str
    ) -> None:
        roles, _ = _SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            account, _ = await self._active_actor(db, actor, roles)
            if not await self.repository.verify_password(db, current, account.account_hash_password):
                raise AccountFormError("current_password", "Mật khẩu hiện tại không đúng")
            if message := helper.password_validation_error(password, password):
                raise AccountFormError("password", message)
            if password == current:
                raise AccountFormError("password", "Mật khẩu mới phải khác mật khẩu hiện tại")
            if password != confirmation:
                raise AccountFormError("password_confirmation", "Mật khẩu nhập lại không khớp")
            account.account_hash_password = await self.repository.hash_password(db, password=password)
            await self.repository.save_account(db, account)
            await self.repository.delete_account_sessions(db, actor.account_key)

    async def _allocate_account_code(self, db, role: Role, values: dict, now) -> str:
        prefix = account_code_prefix(role)
        if role == Role.CUSTOMER:
            date_part = now.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y%m%d")
            body = date_part
        else:
            name = internal_code_name(values["account_name"])
            birth = values["account_date_of_birth"].strftime("%Y%m%d")
            if not 1 <= len(name) <= 83:
                raise AccountFormError("name", "Họ tên không hợp lệ để cấp mã tài khoản nội bộ")
            body = f"{name}-{birth}"
        suffix = await self.repository.next_account_suffix(db, prefix=prefix)
        return f"{prefix}-{body}-{suffix}"

    async def create_managed_account(self, actor: AuthenticatedSession, fields: dict[str, str], password: str) -> None:
        role = self._submitted_role(fields.get("role", ""))
        values = validate_profile(fields, role, creating=True)
        if message := helper.password_validation_error(password, password):
            raise AccountFormError("password", message)
        try:
            async with self.session_factory() as db, transaction(db):
                await self.repository.role_key(db, Role.ADMIN, lock=True)
                await self._active_actor(db, actor, (Role.ADMIN,))
                await self._check_contacts(db, values)
                now = helper.utc_now()
                account = IdentityAccount(
                    **values,
                    account_role_key=await self.repository.role_key(db, role),
                    account_id=await self._allocate_account_code(db, role, values, now),
                    account_hash_password=await self.repository.hash_password(db, password=password),
                    account_created_at=now,
                )
                key = await self.repository.save_account(db, account)
                if role == Role.CUSTOMER:
                    await initialize_customer_shopping(db, account_key=key)
        except IntegrityError as exc:
            self._map_account_integrity_error(exc)

    @staticmethod
    def _submitted_role(value: str) -> Role:
        try:
            return Role(value)
        except ValueError as exc:
            raise AccountFormError("role", "Vai trò không hợp lệ") from exc

    async def _require_remaining_admin(self, db, admin_key: UUID, target: UUID) -> None:
        if not await self.repository.another_active_admin(db, admin_key, target):
            raise AccountFormError("", "Hệ thống phải còn ít nhất một Admin đang hoạt động")

    async def edit_managed_account(self, actor: AuthenticatedSession, key: UUID, fields: dict[str, str]) -> bool:
        try:
            async with self.session_factory() as db, transaction(db):
                admin_key = await self.repository.role_key(db, Role.ADMIN, lock=True)
                await self._active_actor(db, actor, (Role.ADMIN,))
                record = await self.repository.account_record(db, key, lock=True)
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
                values = validate_profile(profile_values(account) | fields, role)
                updates = {column: value for column, value in values.items()
                           if column.removeprefix("account_") in fields}
                await self._check_contacts(db, updates, key)
                account.sqlmodel_update(updates)
                if changed_role:
                    account.account_id = await self._allocate_account_code(db, role, values, helper.utc_now())
                    account.account_role_key = await self.repository.role_key(db, role)
                    await self.repository.delete_account_sessions(db, key)
                await self.repository.save_account(db, account)
                return changed_role
        except IntegrityError as exc:
            self._map_account_integrity_error(exc)

    async def set_account_lock(self, actor: AuthenticatedSession, key: UUID, *, locked: bool) -> None:
        async with self.session_factory() as db, transaction(db):
            admin_key = await self.repository.role_key(db, Role.ADMIN, lock=True)
            roles = (Role.ADMIN, Role.EMPLOYEE) if locked else (Role.ADMIN,)
            _, actor_role = await self._active_actor(db, actor, roles)
            record = await self.repository.account_record(db, key, lock=True)
            if not record or (actor_role == Role.EMPLOYEE and record[1] != Role.CUSTOMER):
                raise SessionAccessError(status_code=403)
            account, role = record
            if locked and role == Role.ADMIN and account.account_status == "ACTIVE":
                await self._require_remaining_admin(db, admin_key, key)
            account.account_status = "LOCKED" if locked else "ACTIVE"
            await self.repository.save_account(db, account)
            if locked:
                await self.repository.delete_account_sessions(db, key)

    async def get_registration_stage(self, browser: str) -> RegistrationResult:
        _, flow = await _read_flow(get_challenge_store(), _flow_key(browser))
        if flow and flow.kind in {"otp", "password", "google_link"}:
            if flow.kind != "password" and flow.attempts <= 0:
                return replace(_locked_otp(flow), status=200)
            return RegistrationResult(flow.kind, email=flow.email)
        return RegistrationResult()


    # UC-01 Đăng ký tài khoản — Main 2–3; E1, E3 (specs/use-cases/identity/UC-01-register-account.md)
    async def start_email_registration(self, browser: str, email: str) -> RegistrationResult:

        try:
            normalized = helper.normalize_email(email)
        except ValueError as exc:
            return RegistrationResult("email", str(exc), email[:255], "email", 400)

        async with self.session_factory() as db, transaction(db):
            if await self.repository.find_account(db, email=normalized) is not None:
                return RegistrationResult("email", _EMAIL_IN_USE, normalized, "email", 409)

        store = get_challenge_store()
        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        if previous and previous.kind == "busy":
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)
        return await _send_challenge(
            store, key, raw, _Flow.new("otp", _OTP_FLOW_SECONDS, email=normalized),
            previous=previous if previous and previous.kind == "otp" and previous.email == normalized else None,
        )


    # UC-01 Đăng ký tài khoản — 4a; E5 (specs/use-cases/identity/UC-01-register-account.md)
    async def resend_email_challenge(self, browser: str) -> RegistrationResult:

        store = get_challenge_store()
        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        if previous is None or previous.kind != "otp":
            return _flow_problem()
        now = helper.utc_timestamp()
        if previous.attempts <= 0 and now < previous.retry_at:
            return _locked_otp(previous)
        if now < previous.expires_at:
            return _flow_problem("otp", _RESEND_EARLY, email=previous.email)

        async with self.session_factory() as db, transaction(db):
            if await self.repository.find_account(db, email=previous.email) is not None:
                await _write_flow(store, key, raw, None)
                return RegistrationResult("email", _EMAIL_IN_USE, previous.email, "email", 409)

        return await _send_challenge(
            store,
            key,
            raw,
            _Flow.new("otp", _OTP_FLOW_SECONDS, email=previous.email),
            previous=previous,
        )


    # UC-01 Đăng ký tài khoản — Main 4–5; E4 (specs/use-cases/identity/UC-01-register-account.md)
    async def verify_registration_email(self, browser: str, otp: str) -> RegistrationResult:
        grant, problem = await _verify_otp(
            get_challenge_store(), _flow_key(browser), "otp", otp, next_kind="password",
            next_seconds=_GRANT_SECONDS,
        )
        return problem or RegistrationResult("password", email=grant.email)


    async def _create_customer(
        self,
        db, *, email: str, password: str | None = None, google_sub: str | None = None
    ) -> None:
        created_at = helper.utc_now()
        registration_day = created_at.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y%m%d")
        password_hash = await self.repository.hash_password(db, password=password) if password is not None else None
        suffix = await self.repository.next_account_suffix(db, prefix="KH")
        account_key = await self.repository.insert_customer(
            db,
            account_id=f"KH-{registration_day}-{suffix}",
            email=email,
            password_hash=password_hash,
            google_sub=google_sub,
            created_at=created_at,
        )
        await initialize_customer_shopping(db, account_key=account_key)


    async def _mark_success(self, store: ChallengeStore, key: str, pending: _Flow) -> RegistrationResult:
        try:
            await _write_flow(store, key, pending.encode(), _Flow.new("registered", _FLASH_SECONDS))
        except Exception as exc:
            # The account has committed. An unavailable flash store must not report a rollback.
            logger.warning("Registration success notice unavailable (%s)", type(exc).__name__)
        return RegistrationResult("registered")


    async def consume_registration_success(self, browser: str) -> bool:
        store = get_challenge_store()
        key = _flow_key(browser)
        raw, flow = await _read_flow(store, key)
        return bool(flow and flow.kind == "registered" and await _write_flow(store, key, raw, None))


    # UC-01 Đăng ký tài khoản — Main 6–8; E1, E6, E7 (specs/use-cases/identity/UC-01-register-account.md)
    async def complete_email_registration(
        self,
        browser: str, password: str, confirmation: str
    ) -> RegistrationResult:

        store = get_challenge_store()
        key = _flow_key(browser)
        raw, grant = await _read_flow(store, key)
        if grant is None or grant.kind != "password":
            return _flow_problem()
        message = helper.password_validation_error(password, confirmation)
        if message:
            return RegistrationResult("password", message, grant.email, "password", 400)

        pending = _Flow.new("busy", _BUSY_SECONDS)
        if not await _write_flow(store, key, raw, pending):
            return _flow_problem()

        try:
            async with self.session_factory() as db, transaction(db):
                exists = await self.repository.find_account(db, email=grant.email) is not None
                if not exists:
                    await self._create_customer(db, email=grant.email, password=password)
        except Exception as exc:
            logger.warning("Email registration rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), grant)
            return _flow_problem("password", _REGISTRATION_FAILED, email=grant.email, status=500)

        if exists:
            await _write_flow(store, key, pending.encode(), None)
            return RegistrationResult("email", _EMAIL_IN_USE, grant.email, "email", 409)
        return await self._mark_success(store, key, pending)


    # UC-01 Đăng ký tài khoản — 1b.1; E8 (specs/use-cases/identity/UC-01-register-account.md)
    async def begin_google_registration(
        self, browser: str, *, allow_create: bool = True, checkout: bool = False
    ) -> RegistrationResult:
        store = get_challenge_store()
        _, previous = await _read_flow(store, _flow_key(browser))
        if previous and previous.kind == "busy":
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)
        flow = _Flow.new(
            "google", _GOOGLE_SECONDS, nonce=token_urlsafe(32), verifier=token_urlsafe(48),
            allow_create=allow_create, checkout=checkout,
        )
        try:
            location = await get_google_oidc().authorization_url(
                state=flow.stamp, nonce=flow.nonce, code_verifier=flow.verifier
            )
        except Exception as exc:
            logger.warning("Google authorization unavailable (%s)", type(exc).__name__)
            return _flow_problem(message=_GOOGLE_FAILED, status=503)
        if not await _write_flow(store, _google_flow_key(browser, flow.stamp), None, flow):
            return _flow_problem(message=_GOOGLE_FAILED)
        return RegistrationResult(location=location)


    async def _issue_session(self, db, account: repository.Account, portal: SessionPortal) -> str:
        token = token_urlsafe(32)
        created_at = helper.utc_now()
        _, lifetime = _SESSION_POLICIES[portal]
        await self.repository.insert_session(
            db,
            account_key=account.account_key,
            token_hash=sha256(token.encode("ascii")).hexdigest(),
            created_at=created_at,
            expires_at=created_at + lifetime,
        )
        return token


    async def _resolve_google(self, identity: GoogleIdentity, *, allow_create: bool) -> RegistrationResult | _Flow:

        async with self.session_factory() as db, transaction(db):
            account = await self.repository.find_account(db, google_sub=identity.sub, for_update=True)
            if account is not None:
                _check_customer(account)
                token = await self._issue_session(db, account, SessionPortal.STOREFRONT)
                return RegistrationResult("signed_in", session_token=token)

            if identity.email_verified is not True:
                raise _GoogleRejected(_GOOGLE_FAILED)
            try:
                email = helper.normalize_email(identity.email)
            except ValueError as exc:
                raise _GoogleRejected(_GOOGLE_FAILED) from exc

            account = await self.repository.find_account(db, email=email)
            if account is not None:
                _check_customer(account)
                if account.google_sub is not None:
                    raise _GoogleRejected(_GOOGLE_FAILED)
                return _Flow.new(
                    "google_link",
                    _OTP_SECONDS,
                    account_key=str(account.account_key),
                    email=account.email,
                    google_sub=identity.sub,
                )

            if not allow_create:
                raise _GoogleRejected(_GOOGLE_ACCOUNT_MISSING)
            await self._create_customer(db, email=email, google_sub=identity.sub)
            return RegistrationResult("registered")


    # UC-01 Đăng ký tài khoản — 1b.2–5; E1, E6, E8 (specs/use-cases/identity/UC-01-register-account.md)
    async def complete_google_registration(
        self,
        browser: str, *, state: str, code: str, provider_error: str
    ) -> RegistrationResult:
        store = get_challenge_store()
        google_key = _google_flow_key(browser, state)
        raw, flow = await _read_flow(store, google_key)
        if flow is None or flow.kind != "google" or not compare_digest(
            flow.stamp.encode("ascii"), state.encode("utf-8")
        ):
            return _flow_problem(message="Lượt xác thực Google đã hết hạn hoặc không còn hiệu lực. Vui lòng bắt đầu lại.")
        if not await _write_flow(store, google_key, raw, None):
            return _flow_problem(message=_GOOGLE_FAILED)
        if provider_error or not code:
            return _flow_problem(message=_GOOGLE_FAILED)

        try:
            identity = await get_google_oidc().exchange_code(
                code=code, nonce=flow.nonce, code_verifier=flow.verifier
            )
        except Exception as exc:
            logger.warning("Google authentication failed (%s)", type(exc).__name__)
            return _flow_problem(message=_GOOGLE_FAILED)

        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        pending = _Flow.new("busy", _BUSY_SECONDS)
        if (previous and previous.kind == "busy") or not await _write_flow(store, key, raw, pending):
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)

        try:
            try:
                result = await self._resolve_google(identity, allow_create=flow.allow_create)
            except IntegrityError as exc:
                if not _google_conflict(exc):
                    raise
                # The failed insert has rolled back. Resolve the winner under existing-account rules.
                result = await self._resolve_google(identity, allow_create=False)
        except _GoogleRejected as exc:
            await _write_flow(store, key, pending.encode(), previous)
            return _flow_problem(message=str(exc))
        except Exception as exc:
            logger.warning("Google registration rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), previous)
            return _flow_problem(message=_REGISTRATION_FAILED, status=500)

        if isinstance(result, _Flow):
            previous_link = previous if (
                previous and previous.kind == "google_link" and previous.email == result.email
            ) else None
            return await _send_challenge(
                store, key, pending.encode(), replace(result, checkout=flow.checkout), previous=previous_link
            )
        if result.stage == "registered":
            return await self._mark_success(store, key, pending)

        await self._clear_completed_flow(store, key, pending)
        return replace(result, checkout=flow.checkout)


    async def _clear_completed_flow(self, store: ChallengeStore, key: str, pending: _Flow) -> None:
        try:
            await _write_flow(store, key, pending.encode(), None)
        except Exception as exc:
            logger.warning("Registration state cleanup failed (%s)", type(exc).__name__)


    # UC-01 Đăng ký tài khoản — E1; UC-02 1d (specs/use-cases/identity/UC-01-register-account.md)
    async def verify_link_and_issue_session(self, browser: str, otp: str) -> RegistrationResult:

        store = get_challenge_store()
        key = _flow_key(browser)
        grant, problem = await _verify_otp(
            store, key, "google_link", otp, next_kind="busy", next_seconds=_BUSY_SECONDS
        )
        if problem:
            return problem

        try:
            async with self.session_factory() as db, transaction(db):
                account = await self.repository.find_account(
                    db, account_key=UUID(grant.account_key), for_update=True
                )
                if account is None or account.email != grant.email or account.google_sub not in {
                    None, grant.google_sub
                }:
                    raise _GoogleRejected(_GOOGLE_FAILED)
                _check_customer(account)
                if account.google_sub is None:
                    await self.repository.link_google_account(
                        db, account_key=account.account_key, google_sub=grant.google_sub
                    )
                token = await self._issue_session(db, account, SessionPortal.STOREFRONT)
        except _GoogleRejected as exc:
            await _write_flow(store, key, grant.encode(), None)
            return _flow_problem(message=str(exc))
        except Exception as exc:
            logger.warning("Google link rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, grant.encode(), None)
            return _flow_problem(message=_GOOGLE_FAILED, status=500)

        await self._clear_completed_flow(store, key, grant)
        return RegistrationResult("signed_in", session_token=token, checkout=grant.checkout)
