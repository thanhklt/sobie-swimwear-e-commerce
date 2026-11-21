from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import DateTime, bindparam, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.modules.identity.session import AuthenticatedSession, Role
from app.shared.web.session import (
    SessionAccessError,
    SessionMiddleware,
    require_roles,
    session_access_error,
)


@pytest.fixture
def session_app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "test-only")
    monkeypatch.setenv("SHIPPING_FEE", "12000")
    monkeypatch.setenv("SEPAY_API_KEY", "test-only")

    from app.shared.database import engine as database

    db_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    monkeypatch.setattr(
        database, "session_factory", async_sessionmaker(db_engine, class_=AsyncSession)
    )

    api = FastAPI()
    api.add_middleware(SessionMiddleware)
    api.add_exception_handler(SessionAccessError, session_access_error)

    @api.get("/customer")
    async def customer(
        session: Annotated[AuthenticatedSession, Depends(require_roles(Role.CUSTOMER))],
    ):
        return {"role": session.role}

    @api.get("/admin/operations")
    async def operations(
        session: Annotated[AuthenticatedSession, Depends(require_roles(Role.EMPLOYEE))],
    ):
        return {"role": session.role}

    @api.get("/admin/accounts")
    async def accounts(
        session: Annotated[AuthenticatedSession, Depends(require_roles(Role.ADMIN))],
    ):
        return {"role": session.role}

    @api.get("/login", name="customer_login")
    async def login():
        return {"page": "login"}

    @api.get("/profile")
    async def profile(
        session: Annotated[
            AuthenticatedSession,
            Depends(require_roles(Role.CUSTOMER, login_route="customer_login")),
        ],
    ):
        return {"role": session.role}

    async def seed_sessions():
        now = datetime.now(UTC)
        old_activity = now - timedelta(minutes=10)
        async with db_engine.begin() as connection:
            await connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS identity")
            await connection.exec_driver_sql(
                "CREATE TABLE identity.role (role_key TEXT PRIMARY KEY, role_code TEXT)"
            )
            await connection.exec_driver_sql(
                "CREATE TABLE identity.account (account_key TEXT PRIMARY KEY, "
                "account_role_key TEXT, account_status TEXT)"
            )
            await connection.exec_driver_sql(
                "CREATE TABLE identity.session (session_key TEXT PRIMARY KEY, "
                "session_account_key TEXT, session_token_hash TEXT UNIQUE, "
                "session_last_seen_at DATETIME, session_expires_at DATETIME)"
            )
            await connection.exec_driver_sql(
                "INSERT INTO identity.role VALUES "
                "('customer', 'customer'), ('employee', 'employee'), ('admin', 'admin')"
            )
            for token, role, status, expiration in (
                ("customer", "customer", "ACTIVE", now + timedelta(minutes=20)),
                ("employee", "employee", "ACTIVE", now + timedelta(minutes=50)),
                ("admin", "admin", "ACTIVE", now + timedelta(minutes=50)),
                ("locked", "customer", "LOCKED", now + timedelta(minutes=20)),
                ("expired", "customer", "ACTIVE", now - timedelta(minutes=1)),
            ):
                account_key = str(uuid4())
                await connection.exec_driver_sql(
                    "INSERT INTO identity.account VALUES (?, ?, ?)",
                    (account_key, role, status),
                )
                await connection.execute(
                    text(
                        "INSERT INTO identity.session VALUES "
                        "(:session_key, :account_key, :token_hash, :seen_at, :expires_at)"
                    ).bindparams(
                        bindparam("seen_at", type_=DateTime(timezone=True)),
                        bindparam("expires_at", type_=DateTime(timezone=True)),
                    ),
                    {
                        "session_key": str(uuid4()),
                        "account_key": account_key,
                        "token_hash": sha256(token.encode()).hexdigest(),
                        "seen_at": old_activity,
                        "expires_at": expiration,
                    },
                )

    async def session_times(token):
        async with db_engine.connect() as connection:
            result = await connection.exec_driver_sql(
                "SELECT session_last_seen_at, session_expires_at "
                "FROM identity.session WHERE session_token_hash = ?",
                (sha256(token.encode()).hexdigest(),),
            )
            return tuple(datetime.fromisoformat(value) for value in result.one())

    with TestClient(api, base_url="https://testserver") as client:
        client.portal.call(seed_sessions)
        try:
            yield client, lambda token: client.portal.call(session_times, token)
        finally:
            client.portal.call(db_engine.dispose)


def test_production_app_registers_session_middleware():
    assert SessionMiddleware in {item.cls for item in app.user_middleware}


@pytest.mark.parametrize(
    "path, cookie_name, token, lifetime",
    [
        ("/customer", "storefront_session", "customer", timedelta(minutes=30)),
        ("/admin/operations", "portal_session", "employee", timedelta(hours=1)),
        ("/admin/accounts", "portal_session", "admin", timedelta(hours=1)),
    ],
)
def test_accepts_allowed_role_and_renews_session(
    session_app, path, cookie_name, token, lifetime
):
    client, session_times = session_app
    previous_seen_at, _ = session_times(token)
    client.cookies.set(cookie_name, token)

    response = client.get(path)
    seen_at, expires_at = session_times(token)

    assert response.status_code == 200
    assert response.json()["role"] == token
    assert seen_at > previous_seen_at
    assert expires_at - seen_at == lifetime


@pytest.mark.parametrize("token", [None, "unknown", "locked", "expired", "employee"])
def test_rejects_invalid_storefront_sessions(session_app, token):
    client, session_times = session_app
    if token:
        client.cookies.set("storefront_session", token)
    stored_session = (
        session_times(token) if token in {"locked", "expired", "employee"} else None
    )

    response = client.get("/customer")

    assert response.status_code == 401
    assert set(response.json()) == {"success", "data", "error", "meta"}
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    if stored_session:
        assert session_times(token) == stored_session


def test_admin_and_employee_permissions_are_distinct(session_app):
    client, _ = session_app

    client.cookies.set("portal_session", "admin")
    response = client.get("/admin/operations")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"

    client.cookies.set("portal_session", "employee")
    assert client.get("/admin/accounts").status_code == 403


def test_only_renews_cookie_for_current_portal(session_app):
    client, session_times = session_app
    client.cookies.set("storefront_session", "customer")
    client.cookies.set("portal_session", "employee")
    storefront_session = session_times("customer")

    assert client.get("/admin/operations").status_code == 200
    assert session_times("customer") == storefront_session


def test_redirects_anonymous_page_request_to_named_login_route(session_app):
    client, _ = session_app

    response = client.get("/profile", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
