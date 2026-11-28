"""Đăng nhập bằng mật khẩu, xác thực, cấp và thu hồi phiên."""

from collections.abc import Callable
from secrets import token_urlsafe

from app.database.transaction import transaction

from ..repository import AccountRepository, ChallengeStore, SessionRepository
from ..schemas import Account, AuthenticatedSession, RegistrationResult, SessionPortal
from . import _rules


class SessionService:
    def __init__(
        self, accounts: AccountRepository, sessions: SessionRepository, session_factory,
        challenge_store: Callable[[], ChallengeStore],
    ):
        self.accounts = accounts
        self.sessions = sessions
        self.session_factory = session_factory
        self.challenge_store = challenge_store

    async def authenticate_session(
        self,
        token: str, portal: SessionPortal
    ) -> AuthenticatedSession | None:
        """Xác thực cookie phía server và gia hạn phiên còn hiệu lực."""
        if not token:
            return None


        allowed_roles, lifetime = _rules.SESSION_POLICIES[portal]
        seen_at = _rules.utc_now()
        token_hash = _rules.hash_token(token)

        async with self.session_factory() as db, transaction(db):
            return await self.sessions.renew_session(
                db,
                token_hash=token_hash,
                allowed_roles=allowed_roles,
                seen_at=seen_at,
                expires_at=seen_at + lifetime,
            )

    async def login_with_password(
        self, identifier: str, password: str, portal: SessionPortal, client_ip: str
    ) -> RegistrationResult:
        ip_key = _rules.hash_token(client_ip)
        if await self.challenge_store().count_password_attempt(ip_key) > 5:
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
                lookup = {"email": _rules.normalize_email(identifier)}
            except ValueError:
                lookup = {"email": identifier}
        else:
            lookup = {"phone": identifier}
        allowed_roles, _ = _rules.SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            account = await self.accounts.find_account(db, for_update=True, **lookup)
            if not account or not await self.accounts.verify_password(db, password, account.password_hash):
                return rejected
            if account.role not in allowed_roles:
                return rejected
            if account.status != "ACTIVE":
                return RegistrationResult(message="Tài khoản đã bị khóa", status=403)
            token = await self.issue_session(db, account, portal)
            return RegistrationResult(stage="signed_in", session_token=token)

    async def logout(self, token: str | None, portal: SessionPortal) -> None:
        if not token:
            return
        roles, _ = _rules.SESSION_POLICIES[portal]
        async with self.session_factory() as db, transaction(db):
            await self.sessions.delete_portal_session(db, _rules.hash_token(token), roles)

    async def issue_session(self, db, account: Account, portal: SessionPortal) -> str:
        token = token_urlsafe(32)
        created_at = _rules.utc_now()
        _, lifetime = _rules.SESSION_POLICIES[portal]
        await self.sessions.insert_session(
            db,
            account_key=account.account_key,
            token_hash=_rules.hash_token(token),
            created_at=created_at,
            expires_at=created_at + lifetime,
        )
        return token
