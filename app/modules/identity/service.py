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
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from hmac import compare_digest, digest
from math import ceil
from secrets import token_urlsafe
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from app.config.settings import Config
from app.database.transaction import transaction
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

    def encode(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))

    @classmethod
    def new(cls, kind: str, seconds: int, **kwargs) -> "_Flow":
        return cls(kind, token_urlsafe(32), helper.utc_timestamp() + seconds, **kwargs)


class _GoogleRejected(Exception):
    """Kết quả xác thực không đáp ứng điều kiện của storefront."""


def _flow_key(browser: str) -> str:
    return "identity:registration:flow:" + sha256(browser.encode("ascii")).hexdigest()


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
        return _flow_problem(
            stage if previous else "email",
            "Không thể gửi mã xác minh. Vui lòng thử lại.",
            email=flow.email,
            status=503,
        )

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
    if flow is None or flow.kind != kind:
        return None, _flow_problem()
    if helper.utc_timestamp() >= flow.expires_at or flow.attempts <= 0:
        return None, _flow_problem(kind, _OTP_INVALID, email=flow.email)

    if len(otp) != 6 or not otp.isascii() or not otp.isdigit() or not compare_digest(
        _otp_digest(flow, otp), flow.otp_digest
    ):
        await _write_flow(store, key, raw, replace(flow, attempts=flow.attempts - 1))
        return None, _flow_problem(kind, _OTP_INVALID, email=flow.email)

    following = _Flow.new(
        next_kind,
        next_seconds,
        email=flow.email,
        account_key=flow.account_key,
        google_sub=flow.google_sub,
    )
    if not await _write_flow(store, key, raw, following):
        return None, _flow_problem(kind, _OTP_INVALID, email=flow.email)
    return following, None


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
        seen_at = datetime.now(UTC)
        token_hash = sha256(token.encode("utf-8")).hexdigest()

        async with self.session_factory() as db, transaction(db):
            return await self.repository.renew_session(
                db,
                token_hash=token_hash,
                allowed_roles=allowed_roles,
                seen_at=seen_at,
                expires_at=seen_at + lifetime,
            )


    async def get_registration_stage(self, browser: str) -> RegistrationResult:
        _, flow = await _read_flow(get_challenge_store(), _flow_key(browser))
        if flow and flow.kind in {"otp", "password", "google_link"}:
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
        if helper.utc_timestamp() < previous.expires_at:
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
    async def begin_google_registration(self, browser: str, *, allow_create: bool = True) -> RegistrationResult:
        store = get_challenge_store()
        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        if previous and previous.kind == "busy":
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)
        flow = _Flow.new(
            "google", _GOOGLE_SECONDS, nonce=token_urlsafe(32), verifier=token_urlsafe(48),
            allow_create=allow_create,
        )
        try:
            location = await get_google_oidc().authorization_url(
                state=flow.stamp, nonce=flow.nonce, code_verifier=flow.verifier
            )
        except Exception as exc:
            logger.warning("Google authorization unavailable (%s)", type(exc).__name__)
            return _flow_problem(message=_GOOGLE_FAILED, status=503)
        if not await _write_flow(store, key, raw, flow):
            return _flow_problem(message=_GOOGLE_FAILED)
        return RegistrationResult(location=location)


    async def _issue_storefront_session(self, db, account: repository.Account) -> str:
        token = token_urlsafe(32)
        created_at = helper.utc_now()
        _, lifetime = _SESSION_POLICIES[SessionPortal.STOREFRONT]
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
                token = await self._issue_storefront_session(db, account)
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
                raise _GoogleRejected(_GOOGLE_FAILED)
            await self._create_customer(db, email=email, google_sub=identity.sub)
            return RegistrationResult("registered")


    # UC-01 Đăng ký tài khoản — 1b.2–5; E1, E6, E8 (specs/use-cases/identity/UC-01-register-account.md)
    async def complete_google_registration(
        self,
        browser: str, *, state: str, code: str, provider_error: str
    ) -> RegistrationResult:
        store = get_challenge_store()
        key = _flow_key(browser)
        raw, flow = await _read_flow(store, key)
        if flow is None or flow.kind != "google" or not compare_digest(
            flow.stamp.encode("ascii"), state.encode("utf-8")
        ):
            return _flow_problem(message=_GOOGLE_FAILED)

        pending = _Flow.new("busy", _BUSY_SECONDS)
        if not await _write_flow(store, key, raw, pending):
            return _flow_problem(message=_GOOGLE_FAILED)
        if provider_error or not code:
            await _write_flow(store, key, pending.encode(), None)
            return _flow_problem(message=_GOOGLE_FAILED)

        try:
            identity = await get_google_oidc().exchange_code(
                code=code, nonce=flow.nonce, code_verifier=flow.verifier
            )
        except Exception as exc:
            logger.warning("Google authentication failed (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), None)
            return _flow_problem(message=_GOOGLE_FAILED)

        try:
            try:
                result = await self._resolve_google(identity, allow_create=flow.allow_create)
            except IntegrityError as exc:
                if not _google_conflict(exc):
                    raise
                # The failed insert has rolled back. Resolve the winner under existing-account rules.
                result = await self._resolve_google(identity, allow_create=False)
        except _GoogleRejected as exc:
            await _write_flow(store, key, pending.encode(), None)
            return _flow_problem(message=str(exc))
        except Exception as exc:
            logger.warning("Google registration rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), None)
            return _flow_problem(message=_REGISTRATION_FAILED, status=500)

        if isinstance(result, _Flow):
            return await _send_challenge(store, key, pending.encode(), result)
        if result.stage == "registered":
            return await self._mark_success(store, key, pending)

        await self._clear_completed_flow(store, key, pending)
        return result


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
                token = await self._issue_storefront_session(db, account)
        except _GoogleRejected as exc:
            await _write_flow(store, key, grant.encode(), None)
            return _flow_problem(message=str(exc))
        except Exception as exc:
            logger.warning("Google link rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, grant.encode(), None)
            return _flow_problem(message=_GOOGLE_FAILED, status=500)

        await self._clear_completed_flow(store, key, grant)
        return RegistrationResult("signed_in", session_token=token)
