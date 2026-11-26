"""Đăng ký tài khoản bằng email và khởi tạo tài khoản Khách hàng."""

import logging
from collections.abc import Callable
from dataclasses import replace
from uuid import UUID
from zoneinfo import ZoneInfo

from app.database.transaction import transaction
from app.modules.shopping.service import initialize_customer_shopping

from ..repository import AccountRepository, ChallengeStore
from ..schemas import RegistrationResult
from . import _rules
from ._otp_flow import (
    _BUSY_SECONDS,
    _EMAIL_IN_USE,
    _OTP_FLOW_SECONDS,
    _REGISTRATION_FAILED,
    _RESEND_EARLY,
    _Flow,
    _flow_key,
    _flow_problem,
    _locked_otp,
    _read_flow,
    _send_challenge,
    _verify_otp,
    _write_flow,
    SendEmail,
    mark_success,
    with_resend_wait,
)

logger = logging.getLogger(__package__)


class EmailRegistrationService:
    def __init__(
        self, accounts: AccountRepository, session_factory,
        challenge_store: Callable[[], ChallengeStore], send_email: SendEmail,
    ):
        self.accounts = accounts
        self.session_factory = session_factory
        self.challenge_store = challenge_store
        self.send_email = send_email

    # UC-01 Main 2–5, AC-18 — Khôi phục bước đăng ký email và thời gian chờ OTP.
    async def get_registration_stage(self, browser: str) -> RegistrationResult:
        store = self.challenge_store()
        _, flow = await _read_flow(store, _flow_key(browser))
        if flow and flow.kind in {"otp", "password"}:
            result = (
                replace(_locked_otp(flow), status=200)
                if flow.kind == "otp" and flow.attempts <= 0
                else RegistrationResult(flow.kind, email=flow.email)
            )
            return await with_resend_wait(store, result)
        return RegistrationResult()

    # UC-01 Đăng ký tài khoản — Main 2–3; E1, E3 (specs/use-cases/identity/UC-01-register-account.md)
    async def start_email_registration(self, browser: str, email: str) -> RegistrationResult:

        try:
            normalized = _rules.normalize_email(email)
        except ValueError as exc:
            return RegistrationResult("email", str(exc), email[:255], "email", 400)

        async with self.session_factory() as db, transaction(db):
            if await self.accounts.find_account(db, email=normalized) is not None:
                return RegistrationResult("email", _EMAIL_IN_USE, normalized, "email", 409)

        store = self.challenge_store()
        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        if previous and previous.kind == "busy":
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)
        result = await _send_challenge(
            store, key, raw, _Flow.new("otp", _OTP_FLOW_SECONDS, email=normalized),
            send_email=self.send_email,
            previous=previous if previous and previous.kind == "otp" and previous.email == normalized else None,
        )
        return await with_resend_wait(store, result)

    # UC-01 Đăng ký tài khoản — 4a; E5 (specs/use-cases/identity/UC-01-register-account.md)
    async def resend_email_challenge(self, browser: str) -> RegistrationResult:

        store = self.challenge_store()
        key = _flow_key(browser)
        raw, previous = await _read_flow(store, key)
        if previous is None or previous.kind != "otp":
            return _flow_problem()
        now = _rules.utc_timestamp()
        if previous.attempts <= 0 and now < previous.retry_at:
            return await with_resend_wait(store, _locked_otp(previous))
        if now < previous.expires_at:
            result = _flow_problem("otp", _RESEND_EARLY, email=previous.email)
            return await with_resend_wait(store, result)

        async with self.session_factory() as db, transaction(db):
            if await self.accounts.find_account(db, email=previous.email) is not None:
                await _write_flow(store, key, raw, None)
                return RegistrationResult("email", _EMAIL_IN_USE, previous.email, "email", 409)

        result = await _send_challenge(
            store,
            key,
            raw,
            _Flow.new("otp", _OTP_FLOW_SECONDS, email=previous.email),
            send_email=self.send_email,
            previous=previous,
        )
        return await with_resend_wait(store, result)

    # UC-01 Đăng ký tài khoản — Main 4–5; E4 (specs/use-cases/identity/UC-01-register-account.md)
    async def verify_registration_email(self, browser: str, otp: str) -> RegistrationResult:
        store = self.challenge_store()
        grant, problem = await _verify_otp(store, _flow_key(browser), otp)
        if problem:
            return await with_resend_wait(store, problem)
        return RegistrationResult("password", email=grant.email)

    # UC-01 Đăng ký tài khoản — Main 6–8; E1, E6, E7 (specs/use-cases/identity/UC-01-register-account.md)
    async def complete_email_registration(
        self,
        browser: str, password: str, confirmation: str
    ) -> RegistrationResult:

        store = self.challenge_store()
        key = _flow_key(browser)
        raw, grant = await _read_flow(store, key)
        if grant is None or grant.kind != "password":
            return _flow_problem()
        message = _rules.password_validation_error(password, confirmation)
        if message:
            return RegistrationResult("password", message, grant.email, "password", 400)

        pending = _Flow.new("busy", _BUSY_SECONDS)
        if not await _write_flow(store, key, raw, pending):
            return _flow_problem()

        try:
            async with self.session_factory() as db, transaction(db):
                exists = await self.accounts.find_account(db, email=grant.email) is not None
                if not exists:
                    await create_customer(self.accounts, db, email=grant.email, password=password)
        except Exception as exc:
            logger.warning("Email registration rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), grant)
            return _flow_problem("password", _REGISTRATION_FAILED, email=grant.email, status=500)

        if exists:
            await _write_flow(store, key, pending.encode(), None)
            return RegistrationResult("email", _EMAIL_IN_USE, grant.email, "email", 409)
        return await mark_success(store, key, pending)

    async def consume_registration_success(self, browser: str) -> bool:
        store = self.challenge_store()
        key = _flow_key(browser)
        raw, flow = await _read_flow(store, key)
        return bool(flow and flow.kind == "registered" and await _write_flow(store, key, raw, None))


async def create_customer(
    accounts: AccountRepository, db, *, email: str, password: str | None = None, google_sub: str | None = None
) -> UUID:
    created_at = _rules.utc_now()
    registration_day = created_at.astimezone(ZoneInfo(_rules.VIETNAM_TIMEZONE)).strftime("%Y%m%d")
    password_hash = await accounts.hash_password(db, password=password) if password is not None else None
    suffix = await accounts.next_account_suffix(db, prefix="KH")
    account_key = await accounts.insert_customer(
        db,
        account_id=f"KH-{registration_day}-{suffix}",
        email=email,
        password_hash=password_hash,
        google_sub=google_sub,
        created_at=created_at,
    )
    await initialize_customer_shopping(db, account_key=account_key)
    return account_key
