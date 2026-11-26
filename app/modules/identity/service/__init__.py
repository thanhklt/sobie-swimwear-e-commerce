"""Lắp ghép các service của module identity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..google_oidc import GoogleOIDC, get_google_oidc
from ..repository import AccountRepository, ChallengeStore, RedisChallengeStore, SessionRepository

if TYPE_CHECKING:
    from redis.asyncio import Redis
from ._otp_flow import SendEmail
from .account import AccountService
from .admin import AdminAccountService
from .auth import SessionService
from .google import GoogleAuthService
from .registration import EmailRegistrationService


@dataclass(frozen=True)
class IdentityServices:
    sessions: SessionService
    registration: EmailRegistrationService
    google: GoogleAuthService
    account: AccountService
    admin: AdminAccountService
    accounts_repository: AccountRepository
    sessions_repository: SessionRepository


def build_identity_services(
    session_factory,
    *,
    send_email: SendEmail,
    redis: Callable[[], Redis] | None = None,
    challenge_store: Callable[[], ChallengeStore] | None = None,
    google_oidc: Callable[[], GoogleOIDC] = get_google_oidc,
    accounts: AccountRepository | None = None,
    sessions: SessionRepository | None = None,
) -> IdentityServices:
    # `redis` là factory lười từ app.redis.engine (như session_factory của database);
    # client chỉ được tạo khi service dùng kho xác minh lần đầu.
    if challenge_store is None:
        if redis is None:
            raise TypeError("build_identity_services requires redis or challenge_store")
        get_redis = redis

        def challenge_store() -> ChallengeStore:
            return RedisChallengeStore(get_redis())
    accounts_repository = accounts if accounts is not None else AccountRepository()
    sessions_repository = sessions if sessions is not None else SessionRepository()
    session_service = SessionService(accounts_repository, sessions_repository, session_factory, challenge_store)
    return IdentityServices(
        sessions=session_service,
        registration=EmailRegistrationService(accounts_repository, session_factory, challenge_store, send_email),
        google=GoogleAuthService(
            accounts_repository, session_service, session_factory, challenge_store, google_oidc
        ),
        account=AccountService(accounts_repository, sessions_repository, session_factory),
        admin=AdminAccountService(accounts_repository, sessions_repository, session_factory),
        accounts_repository=accounts_repository,
        sessions_repository=sessions_repository,
    )
