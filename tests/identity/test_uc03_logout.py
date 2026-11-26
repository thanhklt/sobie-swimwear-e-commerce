"""UC-03 acceptance tests using the PostgreSQL and Redis services in .env."""

from asyncio import Runner
from contextlib import AsyncExitStack
from hashlib import sha256
from http.cookies import SimpleCookie
from ipaddress import IPv6Address
from secrets import randbelow, token_urlsafe
from uuid import uuid4

import httpx
import pytest
from dotenv import dotenv_values
from sqlalchemy import text

from app.config.settings import Config
from app.database.engine import engine
from app.main import app
from app.redis.engine import close_redis, get_redis

ORIGIN = "https://localhost"
STOREFRONT = "/api/v1/identity"
PORTAL = f"{STOREFRONT}/portal"
SITE = {"customer": STOREFRONT, "employee": PORTAL, "admin": PORTAL}
COOKIE = {STOREFRONT: "storefront_session", PORTAL: "portal_session"}
PROTECTED = {STOREFRONT: f"{STOREFRONT}/account/profile", PORTAL: PORTAL}


def digest(value):
    return sha256(value.encode()).hexdigest()


async def sql(query, **params):
    async with engine.begin() as connection:
        result = await connection.execute(text(query), params)
        return result.mappings().all() if result.returns_rows else result.rowcount


async def session_row(token):
    return await sql("""
        SELECT session_last_seen_at, session_expires_at
        FROM identity.session WHERE session_token_hash = :token_hash
    """, token_hash=digest(token))


async def seed_snapshot():
    return await sql("""
        SELECT (SELECT md5(coalesce(string_agg(to_jsonb(a)::text, '' ORDER BY account_key), ''))
                FROM identity.account a) AS accounts,
               (SELECT md5(coalesce(string_agg(to_jsonb(s)::text, '' ORDER BY session_key), ''))
                FROM identity.session s) AS sessions,
               (SELECT md5(string_agg(to_jsonb(c)::text, '' ORDER BY account_prefix))
                FROM identity.account_id_counter c) AS counters
    """)


class LiveLogout:
    def __init__(self):
        self.run_id = uuid4().hex
        self.prefix = f"uc03-pytest-{self.run_id}-"
        self.password = token_urlsafe(24)
        self.accounts = {}
        self.tokens = set()
        self.keys = set()
        self.redis = get_redis()

    async def seed(self):
        for role, prefix in (("customer", "KH"), ("employee", "NV"), ("admin", "AD")):
            key = uuid4()
            email = f"{self.prefix}{role}@example.com"
            code = prefix if role == "customer" else f"{prefix}-{self.run_id.upper()}"
            self.accounts[role] = (key, email)
            [row] = await sql("""
                INSERT INTO identity.account (account_key, account_id, account_role_key, account_email,
                    account_phone_number, account_hash_password, account_name, account_date_of_birth)
                SELECT :key, :account_id, role_key, :email, :phone,
                    crypt(:password, gen_salt('bf', 4)), 'UC03 pytest', DATE '1990-01-01'
                FROM identity.role WHERE role_code = :role RETURNING account_key
            """, key=key, account_id=f"{code}-19900101-{randbelow(10_000):04d}", email=email,
                phone=f"09{randbelow(10**12):012d}", password=self.password, role=role)
            assert row["account_key"] == key

    async def client(self, stack):
        ip = str(IPv6Address("2001:db8::") + (uuid4().int >> 32))
        redis_key = f"identity:password-login:{digest(ip)}"
        assert redis_key not in self.keys and not await self.redis.exists(redis_key)
        self.keys.add(redis_key)
        client = await stack.enter_async_context(httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, client=(ip, 0)), base_url=ORIGIN,
        ))
        return client, redis_key

    async def sign_in(self, client, redis_key, role):
        site = SITE[role]
        before = await self.redis.llen(redis_key)
        response = await client.post(f"{site}/login", headers={"Origin": ORIGIN}, data={
            "identifier": self.accounts[role][1], "password": self.password,
        })
        assert response.status_code == 303
        token = client.cookies[COOKIE[site]]
        self.tokens.add(digest(token))
        assert await self.redis.llen(redis_key) == before + 1
        assert await session_row(token)
        return token

    async def cleanup(self):
        account_keys = [key for key, _ in self.accounts.values()]
        try:
            await sql("""
                DELETE FROM identity.account WHERE account_key = ANY(CAST(:keys AS uuid[]))
                AND account_email LIKE :prefix
            """, keys=account_keys, prefix=f"{self.prefix}%")
        finally:
            if self.keys:
                await self.redis.delete(*self.keys)
        [remaining] = await sql("""
            SELECT (SELECT count(*) FROM identity.account WHERE account_email LIKE :prefix) AS accounts,
                   (SELECT count(*) FROM identity.session
                    WHERE session_account_key = ANY(CAST(:keys AS uuid[]))
                       OR session_token_hash = ANY(CAST(:hashes AS varchar[]))) AS sessions
        """, prefix=f"{self.prefix}%", keys=account_keys, hashes=list(self.tokens))
        redis_remaining = await self.redis.exists(*self.keys) if self.keys else 0
        assert remaining["accounts"] == remaining["sessions"] == redis_remaining == 0
        print("UC-03 pytest cleanup: accounts=0 sessions=0 Redis keys=0")


@pytest.fixture(scope="module")
def live_logout():
    dotenv = dotenv_values(".env")
    assert Config.DATABASE_URL == dotenv["DATABASE_URL"] and Config.REDIS_URL == dotenv["REDIS_URL"]
    with Runner() as runner:
        live = LiveLogout()
        try:
            [server] = runner.run(sql("SELECT current_database() AS name"))
            assert server["name"] == "sobieDB" and runner.run(live.redis.ping())
            baseline = runner.run(seed_snapshot())
            try:
                runner.run(live.seed())
                yield runner, live
            finally:
                runner.run(live.cleanup())
                assert runner.run(seed_snapshot()) == baseline
                print("UC-03 pytest cleanup: pre-existing accounts, sessions and counters unchanged")
        finally:
            runner.run(close_redis())
            runner.run(engine.dispose())


async def post(client, site, *, headers=None):
    return await client.post(f"{site}/logout", headers={"Origin": ORIGIN} if headers is None else headers)


def assert_logout(response, site):
    assert response.status_code == 303 and response.headers["location"] == "/"
    assert response.headers["cache-control"] == "no-store"
    cookies = SimpleCookie()
    for header in response.headers.get_list("set-cookie"):
        cookies.load(header)
    assert set(cookies) == {COOKIE[site]}
    cookie = cookies[COOKIE[site]]
    assert cookie.value == "" and cookie["max-age"] == "0" and cookie["path"] == "/"
    assert cookie["secure"] and cookie["httponly"] and cookie["samesite"] == "lax"


def assert_login_required(response, site):
    assert response.status_code == 303 and response.headers["location"] == f"{site}/login"
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("role", SITE)
def test_uc03_ac1_ac2_ac4_logout_revokes_only_current_session(live_logout, role):
    runner, live = live_logout
    site = SITE[role]
    other_role = "employee" if role == "customer" else "customer"
    other_site = SITE[other_role]

    async def verify():
        async with AsyncExitStack() as stack:
            client, key = await live.client(stack)
            device, device_key = await live.client(stack)
            fresh, _ = await live.client(stack)
            token = await live.sign_in(client, key, role)
            other_token = await live.sign_in(client, key, other_role)
            same_role_token = await live.sign_in(device, device_key, role)
            siblings = (await session_row(other_token), await session_row(same_role_token))

            misplaced = await post(fresh, other_site, headers={
                "Origin": ORIGIN, "Cookie": f"{COOKIE[other_site]}={token}",
            })
            assert_logout(misplaced, other_site)
            assert await session_row(token)

            assert_logout(await post(client, site), site)
            assert not await session_row(token)
            assert client.cookies.get(COOKIE[site]) is None
            assert client.cookies[COOKIE[other_site]] == other_token
            assert (await session_row(other_token), await session_row(same_role_token)) == siblings

            assert_login_required(await client.get(PROTECTED[site]), site)
            replay = await fresh.get(PROTECTED[site], headers={"Cookie": f"{COOKIE[site]}={token}"})
            assert_login_required(replay, site)
            assert (await client.get(PROTECTED[other_site])).status_code == 200
            assert (await device.get(PROTECTED[site])).status_code == 200

    runner.run(verify())


@pytest.mark.parametrize("role", SITE)
def test_uc03_ac3_logout_expired_session_is_idempotent(live_logout, role):
    runner, live = live_logout
    site = SITE[role]

    async def verify():
        async with AsyncExitStack() as stack:
            client, key = await live.client(stack)
            token = await live.sign_in(client, key, role)
            assert await sql("""
                UPDATE identity.session SET session_created_at = now() - interval '2 hours',
                    session_last_seen_at = now() - interval '2 hours', session_expires_at = now() - interval '1 hour'
                WHERE session_token_hash = :token_hash
            """, token_hash=digest(token)) == 1
            assert_logout(await post(client, site), site)
            assert not await session_row(token)
            assert client.cookies.get(COOKIE[site]) is None
            assert_logout(await post(client, site), site)
            assert_logout(await post(client, site, headers={
                "Origin": ORIGIN, "Cookie": f"{COOKIE[site]}={token}",
            }), site)

    runner.run(verify())
