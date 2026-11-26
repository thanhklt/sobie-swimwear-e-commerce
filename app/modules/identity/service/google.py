"""Đăng ký, đăng nhập và liên kết tài khoản qua Google OIDC."""

import logging
from collections.abc import Callable
from dataclasses import replace
from hmac import compare_digest
from secrets import token_urlsafe

from sqlalchemy.exc import IntegrityError

from app.database.transaction import transaction

from ..google_oidc import GoogleIdentity, GoogleOIDC
from ..repository import AccountRepository, ChallengeStore
from ..schemas import Account, RegistrationResult, Role, SessionPortal
from . import _rules
from ._otp_flow import (
    _BUSY_SECONDS,
    _GOOGLE_FAILED,
    _GOOGLE_SECONDS,
    _REGISTRATION_FAILED,
    _Flow,
    _flow_key,
    _flow_problem,
    _google_flow_key,
    _read_flow,
    _write_flow,
    clear_completed_flow,
)
from .auth import SessionService
from .registration import create_customer

logger = logging.getLogger(__package__)


class GoogleAuthService:
    def __init__(
        self, accounts: AccountRepository, sessions: SessionService, session_factory,
        challenge_store: Callable[[], ChallengeStore], google_oidc: Callable[[], GoogleOIDC],
    ):
        self.accounts = accounts
        self.sessions = sessions
        self.session_factory = session_factory
        self.challenge_store = challenge_store
        self.google_oidc = google_oidc

    # UC-01 1b.1; UC-02 1a, 1c — Khởi tạo cùng luồng Google từ đăng ký hoặc đăng nhập.
    async def begin_google_registration(
        self, browser: str, *, checkout: bool = False
    ) -> RegistrationResult:
        store = self.challenge_store()
        _, previous = await _read_flow(store, _flow_key(browser))
        if previous and previous.kind == "busy":
            return _flow_problem(message="Yêu cầu đang được xử lý. Vui lòng thử lại.", status=409)
        flow = _Flow.new(
            "google", _GOOGLE_SECONDS, nonce=token_urlsafe(32), verifier=token_urlsafe(48),
            checkout=checkout,
        )
        try:
            location = await self.google_oidc().authorization_url(
                state=flow.stamp, nonce=flow.nonce, code_verifier=flow.verifier
            )
        except Exception as exc:
            logger.warning("Google authorization unavailable (%s)", type(exc).__name__)
            return _flow_problem(message=_GOOGLE_FAILED, status=503)
        if not await _write_flow(store, _google_flow_key(browser, flow.stamp), None, flow):
            return _flow_problem(message=_GOOGLE_FAILED)
        return RegistrationResult(location=location)

    # UC-01 1b.2–5, E1, E6, E8; UC-02 1a, 1c, 1d, E6 — Cấp phiên ngay sau xác thực Google.
    async def complete_google_registration(
        self,
        browser: str, *, state: str, code: str, provider_error: str
    ) -> RegistrationResult:
        store = self.challenge_store()
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
            identity = await self.google_oidc().exchange_code(
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
                result = await self._resolve_google(identity)
            except IntegrityError as exc:
                if not _google_conflict(exc):
                    raise
                # The failed write has rolled back. Resolve the account that won the race.
                result = await self._resolve_google(identity)
        except _GoogleRejected as exc:
            await _write_flow(store, key, pending.encode(), previous)
            return _flow_problem(message=str(exc))
        except Exception as exc:
            logger.warning("Google registration rolled back (%s)", type(exc).__name__)
            await _write_flow(store, key, pending.encode(), previous)
            return _flow_problem(message=_REGISTRATION_FAILED, status=500)

        await clear_completed_flow(store, key, pending)
        return replace(result, checkout=flow.checkout)

    async def _resolve_google(self, identity: GoogleIdentity) -> RegistrationResult:
        if identity.email_verified is not True:
            raise _GoogleRejected(_GOOGLE_FAILED)

        async with self.session_factory() as db, transaction(db):
            account = await self.accounts.find_account(db, google_sub=identity.sub, for_update=True)
            if account is None:
                try:
                    email = _rules.normalize_email(identity.email)
                except ValueError as exc:
                    raise _GoogleRejected(_GOOGLE_FAILED) from exc
                account = await self.accounts.find_account(db, email=email, for_update=True)

            if account is None:
                account_key = await create_customer(self.accounts, db, email=email, google_sub=identity.sub)
                account = await self.accounts.find_account(db, account_key=account_key)
                if account is None:
                    raise RuntimeError("The newly created customer could not be loaded")
            else:
                _check_customer(account)
                if account.google_sub is None:
                    await self.accounts.link_google_account(
                        db, account_key=account.account_key, google_sub=identity.sub
                    )
                elif account.google_sub != identity.sub:
                    raise _GoogleRejected(_GOOGLE_FAILED)

            token = await self.sessions.issue_session(db, account, SessionPortal.STOREFRONT)
            return RegistrationResult("signed_in", session_token=token)


class _GoogleRejected(Exception):
    """Kết quả xác thực không đáp ứng điều kiện của storefront."""


def _check_customer(account: Account) -> None:
    if account.role != Role.CUSTOMER:
        raise _GoogleRejected("Thông tin đăng nhập không đúng")
    if account.status != "ACTIVE":
        raise _GoogleRejected("Tài khoản đã bị khóa")


def _google_conflict(exc: IntegrityError) -> bool:
    # asyncpg wraps the PostgreSQL constraint error in its DBAPI adapter.
    constraint = getattr(getattr(exc.orig, "__cause__", None), "constraint_name", None)
    return constraint in {"account_account_email_key", "account_account_google_sub_key"}
