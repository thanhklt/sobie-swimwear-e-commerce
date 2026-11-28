"""Lượt xác minh, OTP và thông báo đăng ký lưu trong Redis."""

import json
import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from hmac import compare_digest, digest
from math import ceil
from secrets import randbelow, token_urlsafe

from app.config.settings import Config

from ..repository import ChallengeStore
from ..schemas import RegistrationResult
from . import _otp_flow, _rules

SendEmail = Callable[[str, str, Mapping[str, object]], Awaitable[None]]


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
_RESTART = "Lượt xác minh đã hết hạn. Vui lòng bắt đầu lại."

logger = logging.getLogger(__package__)


def generate_otp() -> str:
    return f"{randbelow(1_000_000):06d}"


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
    allow_create: bool = True  # Giữ để đọc các lượt OIDC cũ trong Redis.
    retry_at: float = 0
    checkout: bool = False

    def encode(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))

    @classmethod
    def new(cls, kind: str, seconds: int, **kwargs) -> "_Flow":
        return cls(kind, token_urlsafe(32), _rules.utc_timestamp() + seconds, **kwargs)


def _flow_key(browser: str) -> str:
    return "identity:registration:flow:" + sha256(browser.encode("ascii")).hexdigest()


def _google_flow_key(browser: str, state: str) -> str:
    value = sha256(f"{browser}:{state}".encode("utf-8")).hexdigest()
    return f"identity:registration:google:{value}"


def _cooldown_key(purpose: str, email: str) -> str:
    return f"identity:registration:cooldown:{purpose}:" + sha256(
        email.lower().encode("utf-8")
    ).hexdigest()


async def with_resend_wait(store: ChallengeStore, result: RegistrationResult) -> RegistrationResult:
    if result.stage == "otp" and result.email:
        return replace(result, resend_after=await store.ttl(_cooldown_key("otp", result.email)))
    return result


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
    return raw, flow if flow.retain_until > _rules.utc_timestamp() else None


async def _write_flow(
    store: ChallengeStore, key: str, expected: str | None, flow: _Flow | None
) -> bool:
    if flow is None:
        return await store.compare_and_set(key, expected, None)
    ttl = ceil(flow.retain_until - _rules.utc_timestamp())
    if ttl <= 0:
        return False
    return await store.compare_and_set(key, expected, flow.encode(), ttl)


def _flow_problem(
    stage: str = "email", message: str = _RESTART, *, email: str = "", status: int = 400
) -> RegistrationResult:
    return RegistrationResult(stage, message, email, status=status)


def _locked_otp(flow: _Flow) -> RegistrationResult:
    if _rules.utc_timestamp() < flow.retry_at:
        message = "Bạn đã nhập sai mã 5 lần. Hãy chờ đủ 5 phút kể từ lần sai cuối rồi yêu cầu mã mới."
    else:
        message = "Mã này đã bị khóa sau 5 lần nhập sai. Hãy yêu cầu mã mới."
    return RegistrationResult(flow.kind, message, flow.email, status=429, otp_locked=True)


async def _send_challenge(
    store: ChallengeStore,
    key: str,
    expected: str | None,
    flow: _Flow,
    *,
    send_email: SendEmail,
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

    otp = _otp_flow.generate_otp()
    while previous and compare_digest(_otp_digest(previous, otp), previous.otp_digest):
        otp = _otp_flow.generate_otp()

    try:
        await send_email(flow.email, "registration_otp", {"otp": otp})
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

    sent_at = _rules.utc_timestamp()
    challenge = replace(
        flow,
        otp_digest=_otp_digest(flow, otp),
        attempts=_OTP_TRIES,
        expires_at=sent_at + _OTP_SECONDS,
        retain_until=sent_at + _OTP_FLOW_SECONDS,
    )
    # The cooldown is counted from successful SMTP delivery, including across browsers.
    if not await store.compare_and_set(cooldown, claim, claim, _OTP_SECONDS):
        raise RuntimeError("The OTP delivery reservation expired")
    if not await _write_flow(store, key, pending.encode(), challenge):
        raise RuntimeError("The registration challenge expired during delivery")
    return RegistrationResult(stage, "Đã gửi mã xác minh.", flow.email)


async def _verify_otp(
    store: ChallengeStore, key: str, otp: str
) -> tuple[_Flow | None, RegistrationResult | None]:
    raw, flow = await _read_flow(store, key)
    if raw is None or flow is None or flow.kind != "otp":
        return None, _flow_problem()
    stamp = flow.stamp
    invalid = _flow_problem("otp", _OTP_INVALID, email=flow.email)
    matches = len(otp) == 6 and otp.isascii() and otp.isdigit() and compare_digest(
        _otp_digest(flow, otp), flow.otp_digest
    )
    while raw is not None and flow is not None and flow.kind == "otp" and flow.stamp == stamp:
        now = _rules.utc_timestamp()
        if flow.attempts <= 0:
            return None, _locked_otp(flow)
        if now >= flow.expires_at:
            break

        if matches:
            following = _Flow.new("password", _GRANT_SECONDS, email=flow.email)
            if await _write_flow(store, key, raw, following):
                return following, None
        elif flow.attempts == 1:
            retry_at = now + _OTP_LOCK_SECONDS
            locked = replace(flow, attempts=0, retry_at=retry_at,
                             retain_until=max(flow.retain_until, retry_at + _OTP_SECONDS))
            if await store.exhaust_otp(
                key, raw, locked.encode(), ceil(locked.retain_until - now),
                cooldown_key=_cooldown_key("otp", flow.email), cooldown_seconds=_OTP_LOCK_SECONDS,
            ):
                return None, _locked_otp(locked)
        elif await _write_flow(store, key, raw, replace(flow, attempts=flow.attempts - 1)):
            return None, invalid

        # A concurrent update may have charged another attempt. Retry only against the same OTP.
        raw, flow = await _read_flow(store, key)
    return None, invalid


async def mark_success(store: ChallengeStore, key: str, pending: _Flow) -> RegistrationResult:
    try:
        await _write_flow(store, key, pending.encode(), _Flow.new("registered", _FLASH_SECONDS))
    except Exception as exc:
        # The account has committed. An unavailable flash store must not report a rollback.
        logger.warning("Registration success notice unavailable (%s)", type(exc).__name__)
    return RegistrationResult("registered")


async def clear_completed_flow(store: ChallengeStore, key: str, pending: _Flow) -> None:
    try:
        await _write_flow(store, key, pending.encode(), None)
    except Exception as exc:
        logger.warning("Registration state cleanup failed (%s)", type(exc).__name__)
