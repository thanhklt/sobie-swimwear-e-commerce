"""UC-01 acceptance fixture backed by a dedicated PostgreSQL database."""
import asyncio
import os
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from types import SimpleNamespace
from urllib.parse import urlparse
from uuid import UUID, uuid4

import asyncpg
import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.fixture
def world(monkeypatch):
    from app.main import app
    from app.modules.identity import google_oidc, helper, service
    from app.modules.identity.session import AuthenticatedSession, Role
    from app.modules.shopping import repository as shopping

    dsn = os.environ["UC01_TEST_DATABASE_URL"]
    if urlparse(dsn).path != "/uc01test":
        raise RuntimeError("UC01_TEST_DATABASE_URL must point to the dedicated uc01test database")
    engine = create_async_engine(dsn.replace("postgresql://", "postgresql+asyncpg://"), poolclass=NullPool)
    monkeypatch.setattr(app.state.identity_service, "session_factory", async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    ))

    async def run_sql(query, *args, fetch=True):
        connection = await asyncpg.connect(dsn)
        try:
            return await connection.fetch(query, *args) if fetch else await connection.execute(query, *args)
        finally:
            await connection.close()

    def sql(query, *args, fetch=True):
        return asyncio.run(run_sql(query, *args, fetch=fetch))

    sql("TRUNCATE identity.account CASCADE", fetch=False)
    sql("UPDATE identity.account_id_counter SET last_number = 0 WHERE account_prefix = 'KH'", fetch=False)

    w = SimpleNamespace(mail=[], now=datetime(2026, 11, 23, 18, 0, tzinfo=UTC), failure=None, sql=sql)
    w.advance = lambda seconds: setattr(w, "now", w.now + timedelta(seconds=seconds))
    monkeypatch.setattr(helper, "utc_now", lambda: w.now)
    otp_numbers = iter(range(100000, 200000))
    monkeypatch.setattr(helper, "generate_otp", lambda: str(next(otp_numbers)))

    class Store:
        def __init__(self):
            self.values = {}
            self.attempts = {}

        async def count_password_attempt(self, ip_key):
            recent = [sent for sent in self.attempts.get(ip_key, ()) if w.now - sent < timedelta(seconds=60)]
            if len(recent) >= 5:
                return 6
            self.attempts[ip_key] = recent + [w.now]
            return len(recent) + 1

        async def get(self, key):
            entry = self.values.get(key)
            if entry and entry[1] <= w.now:
                self.values.pop(key, None)
                return None
            return entry[0] if entry else None

        async def compare_and_set(self, key, expected, value, ttl=0):
            if await self.get(key) != expected:
                return False
            if value is None:
                self.values.pop(key, None)
            else:
                self.values[key] = (value, w.now + timedelta(seconds=ttl))
            return True

        async def exhaust_otp(self, key, expected, value, ttl, *, cooldown_key, cooldown_seconds):
            if not await self.compare_and_set(key, expected, value, ttl):
                return False
            deadline = w.now + timedelta(seconds=cooldown_seconds)
            current = self.values.get(cooldown_key)
            if current is None or current[1] < deadline:
                self.values[cooldown_key] = ((current[0] if current else "locked"), deadline)
            return True

    store = Store()
    monkeypatch.setattr(service, "get_challenge_store", lambda: store)

    async def mail(email, otp):
        w.mail.append((email, otp))
    monkeypatch.setattr(service, "send_registration_otp", mail)

    class OIDC:
        failure = None

        async def authorization_url(self, *, state, nonce, code_verifier):
            return f"https://google.example/authorize?state={state}"

        async def exchange_code(self, *, code, nonce, code_verifier):
            if self.failure in ("cancel", "invalid"):
                raise ValueError("invalid Google response")
            return google_oidc.GoogleIdentity(
                sub="google-sub", email="google@example.com",
                email_verified=self.failure != "unverified"
            )

    w.oidc = OIDC()
    monkeypatch.setattr(service, "get_google_oidc", lambda: w.oidc)

    def fail(name):
        if w.failure == name:
            raise RuntimeError(f"injected {name} failure")

    identity_repository = app.state.identity_service.repository
    for method_name, failure_name in (
        ("next_account_suffix", "suffix"), ("insert_customer", "account"),
        ("insert_session", "session"), ("delete_account_sessions", "revoke"),
        ("save_account", "save_account"),
    ):
        original = getattr(identity_repository, method_name)

        def wrapper_factory(fn, point):
            async def wrapper(*args, **kwargs):
                result = await fn(*args, **kwargs)
                fail(point)
                return result
            return wrapper

        monkeypatch.setattr(identity_repository, method_name, wrapper_factory(original, failure_name))

    for method_name, failure_name in (("insert_cart", "cart"), ("insert_wishlist", "wishlist")):
        original = getattr(shopping, method_name)

        def wrapper_factory(fn, point):
            async def wrapper(*args, **kwargs):
                result = await fn(*args, **kwargs)
                fail(point)
                return result
            return wrapper

        monkeypatch.setattr(shopping, method_name, wrapper_factory(original, failure_name))

    w.client = TestClient(app, base_url="https://testserver")
    w.new_client = lambda: TestClient(app, base_url="https://testserver")
    w.client_without_server_exceptions = lambda: TestClient(
        app, base_url="https://testserver", raise_server_exceptions=False
    )

    def counts():
        tables = ("identity.account", "shopping.cart", "shopping.wishlist")
        return tuple(sql(f"SELECT count(*) FROM {table}")[0][0] for table in tables) + (
            sql("SELECT last_number FROM identity.account_id_counter WHERE account_prefix = 'KH'")[0][0],
        )
    w.counts = counts

    def seed(email, google_sub=None):
        account = sql(
            """INSERT INTO identity.account
               (account_id, account_role_key, account_email, account_hash_password, account_google_sub)
               SELECT 'KH-20261124-0999', role_key, $1, crypt('123456', gen_salt('bf', 4)), $2
               FROM identity.role WHERE role_code = 'customer' RETURNING account_key""",
            email, google_sub,
        )[0][0]
        sql("INSERT INTO shopping.cart (cart_account_key) VALUES ($1)", account, fetch=False)
        sql("INSERT INTO shopping.wishlist (wishlist_account_key) VALUES ($1)", account, fetch=False)
        return str(account)
    w.seed_account = seed

    def seed_member(email, *, role="customer", phone=None, status="ACTIVE", google_sub=None, password=True):
        prefixes = {
            "customer": "KH-20261124", "employee": "NV-SOBIETEST-19950101", "admin": "AD-SOBIETEST-19950101",
        }
        seed_member.count += 1
        return sql(
            """INSERT INTO identity.account (
                   account_id, account_role_key, account_email, account_phone_number,
                   account_hash_password, account_status, account_google_sub, account_name,
                   account_date_of_birth
               )
               SELECT $1, role_key, $2, $3, CASE WHEN $4 THEN crypt('123456', gen_salt('bf', 4)) END,
                   $5, $6, 'Sobie Test', DATE '1995-01-01'
               FROM identity.role WHERE role_code = $7 RETURNING account_key""",
            f"{prefixes[role]}-{9000 + seed_member.count:04d}", email, phone, password,
            status, google_sub, role,
        )[0][0]

    seed_member.count = 0
    w.seed_member = seed_member

    def authenticated():
        async def auth(token, portal):
            return AuthenticatedSession(uuid4(), uuid4(), Role.CUSTOMER)
        monkeypatch.setattr(app.state.identity_service, "authenticate_session", auth)
        w.client.cookies.set("storefront_session", "test", domain="testserver.local", path="/")
    w.authenticated = authenticated

    def assert_new_account(email, password=None, google_sub=None, suffix="0001"):
        row = sql("""SELECT account_key, account_id, account_email, account_hash_password,
                            account_google_sub, account_status, account_name, account_phone_number,
                            account_date_of_birth, account_house_number, account_ward, account_city,
                            account_country, role_code
                     FROM identity.account JOIN identity.role ON role_key = account_role_key
                     WHERE account_email = $1""", email)
        assert len(row) == 1
        item = row[0]
        assert item["account_id"] == f"KH-20261124-{suffix}"
        assert item["account_email"] == email and item["account_google_sub"] == google_sub
        assert item["account_status"] == "ACTIVE" and item["role_code"] == "customer"
        assert all(item[name] is None for name in (
            "account_name", "account_phone_number", "account_date_of_birth", "account_house_number",
            "account_ward", "account_city", "account_country"
        ))
        if password:
            assert bcrypt.checkpw(password.encode(), item["account_hash_password"].encode())
            assert not bcrypt.checkpw(b"incorrect-password", item["account_hash_password"].encode())
        else:
            assert item["account_hash_password"] is None
        assert w.counts()[:3] == (1, 1, 1)
        assert sql("SELECT cart_account_key FROM shopping.cart")[0][0] == item["account_key"]
        assert sql("SELECT wishlist_account_key FROM shopping.wishlist")[0][0] == item["account_key"]
        assert sql("SELECT count(*) FROM shopping.cart_item")[0][0] == 0
        assert sql("SELECT count(*) FROM shopping.wishlist_item")[0][0] == 0
    w.assert_new_account = assert_new_account
    w.session_account = lambda: str(sql("SELECT session_account_key FROM identity.session WHERE session_token_hash=$1",
        sha256(w.client.cookies["storefront_session"].encode()).hexdigest())[0][0])
    w.google_sub = lambda account: sql("SELECT account_google_sub FROM identity.account WHERE account_key=$1",
        UUID(account))[0][0]
    w.session_lifetime = lambda: sql(
        "SELECT extract(epoch FROM session_expires_at-session_created_at) FROM identity.session")[0][0]

    @contextmanager
    def fail_at(name):
        w.failure = name
        try:
            yield
        finally:
            w.failure = None
    w.fail_at = fail_at
    yield w
    w.client.close()
    asyncio.run(engine.dispose())
