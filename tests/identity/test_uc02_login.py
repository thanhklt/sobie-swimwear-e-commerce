from html import unescape
import re
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import pytest

from identity_support import google, login, post, signed_in


PREFIX = "/api/v1/identity"
LOGIN = f"{PREFIX}/login"
PORTAL_LOGIN = f"{PREFIX}/portal/login"
CHECKOUT = "/api/v1/ordering/checkout"
MERGE = "/api/v1/shopping/cart/merge"


@pytest.mark.parametrize("role, portal, by_phone", [
    ("customer", False, False), ("customer", False, True),
    ("employee", True, False), ("admin", True, False),
])
def test_uc02_ac1_ac2_ac3_password_login(world, role, portal, by_phone):
    world.seed_member("member@example.com", role=role, phone="0981234567")
    client = world.new_client()
    response = login(client, "0981234567" if by_phone else "MEMBER@example.com", portal=portal)
    assert response.status_code == 303 and response.headers["location"] == ("/api/v1/identity/portal" if portal else "/")
    cookie = "portal_session" if portal else "storefront_session"
    header = response.headers.get_list("set-cookie")
    assert any(cookie + "=" in entry and all(flag in entry.lower() for flag in ("secure", "httponly", "samesite=lax"))
               for entry in header)
    rows = world.sql("SELECT session_expires_at - session_created_at AS lifetime FROM identity.session")
    assert rows[0]["lifetime"].total_seconds() == (3600 if portal else 1800)

    if portal:
        existing = client.get("/api/v1/identity/portal/login", follow_redirects=False)
        assert existing.status_code == 303 and existing.headers["location"] == "/api/v1/identity/portal"
        overview = client.get(response.headers["location"])
        title, link = (
            ("Tổng quan Admin", "/api/v1/identity/portal/accounts")
            if role == "admin" else ("Tổng quan Nhân viên", "/api/v1/identity/portal/customers")
        )
        assert overview.status_code == 200 and overview.headers["cache-control"] == "no-store"
        assert title in overview.text and f'href="{link}"' in overview.text
        assert overview.url.path == "/api/v1/identity/portal"


@pytest.mark.parametrize("role,status,password,portal,identifier,code,message", [
    ("customer", "ACTIVE", "wrong", False, "member@example.com", 401, "Thông tin đăng nhập không đúng"),
    ("customer", "ACTIVE", "123456", False, "missing@example.com", 401, "Thông tin đăng nhập không đúng"),
    ("customer", "LOCKED", "123456", False, "member@example.com", 403, "Tài khoản đã bị khóa"),
    ("admin", "ACTIVE", "123456", False, "member@example.com", 401, "Thông tin đăng nhập không đúng"),
    ("customer", "ACTIVE", "123456", True, "member@example.com", 401, "Thông tin đăng nhập không đúng"),
    ("google", "ACTIVE", "123456", False, "member@example.com", 401, "Thông tin đăng nhập không đúng"),
])
def test_uc02_ac4_ac5_ac6_ac8_ac9_ac18_rejected_password(world, role, status, password, portal, identifier, code, message):
    world.seed_member("member@example.com", role="customer" if role == "google" else role,
                      phone="0981234567", status=status, password=role != "google",
                      google_sub="google-sub" if role == "google" else None)
    response = login(world.client, identifier, password, portal=portal)
    assert response.status_code == code and message in response.text
    assert not world.sql("SELECT 1 FROM identity.session")


def test_uc02_ac10_forgot_password_is_storefront_only(world):
    assert 'type="button">Quên mật khẩu' in world.client.get("/api/v1/identity/login").text
    assert "Quên mật khẩu" not in world.client.get("/api/v1/identity/portal/login").text


def test_uc02_ac11_ac12_idle_expiry_and_renewal(world):
    world.seed_member("member@example.com")
    client = signed_in(world, "member@example.com")
    world.advance(1799)
    assert client.get("/api/v1/identity/account/profile").status_code == 200
    world.advance(1799)
    assert client.get("/api/v1/identity/account/profile").status_code == 200
    world.advance(1800)
    response = client.get("/api/v1/identity/account/profile", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/api/v1/identity/login"


def test_uc02_ac13_ac19_rate_limit_and_google(world):
    world.seed_member("google@example.com", google_sub="google-sub", password=False)
    for _ in range(5):
        assert login(world.client, "missing@example.com").status_code == 401
    assert login(world.client, "missing@example.com", portal=True).status_code == 429
    client = world.new_client()
    assert google(client, world.oidc, login_only=True).status_code == 303
    assert client.cookies.get("storefront_session")
    world.advance(60)
    assert login(world.new_client(), "missing@example.com").status_code == 401


@pytest.mark.parametrize("scenario", ["linked", "locked", "missing", "link", "invalid_otp", "cancel"])
def test_uc02_ac14_ac15_ac16_ac17_ac21_google(world, scenario):
    key = None
    if scenario in {"linked", "locked", "link", "invalid_otp"}:
        key = world.seed_member(
            "google@example.com", google_sub="google-sub" if scenario in {"linked", "locked"} else None,
            status="LOCKED" if scenario == "locked" else "ACTIVE", password=scenario != "linked",
        )
    world.oidc.failure = "cancel" if scenario == "cancel" else None
    response = google(world.client, world.oidc, login_only=True)
    if scenario in {"link", "invalid_otp"}:
        assert world.mail and world.mail[-1][0] == "google@example.com"
        code = world.mail[-1][1] if scenario == "link" else "abcdef"
        response = post(world.client, "/api/v1/identity/register/google/link/otp", otp=code)
    sessions = world.sql("SELECT session_account_key FROM identity.session")
    if scenario in {"linked", "link"}:
        assert response.status_code == 303 and world.client.cookies.get("storefront_session")
        assert [row[0] for row in sessions] == [key]
        assert world.google_sub(str(key)) == "google-sub"
    else:
        assert not world.client.cookies.get("storefront_session") and not sessions
        if scenario == "locked":
            assert "Tài khoản đã bị khóa" in response.text
        if scenario == "missing":
            assert "Email Google này chưa có tài khoản Sobie" in response.text
            assert "Đăng ký với Google" in response.text
        if scenario == "invalid_otp":
            assert world.google_sub(str(key)) is None
        if key is None:
            assert not world.sql("SELECT 1 FROM identity.account")


def test_uc02_ac22_google_link_otp_requires_new_code_after_lock(world):
    world.seed_member("google@example.com")
    client = world.client
    google(client, world.oidc, login_only=True)
    old = world.mail[-1][1]
    verify_url = "/api/v1/identity/register/google/link/otp"
    world.advance(15)
    for _ in range(4):
        page = post(client, verify_url, otp="000000")
        assert page.status_code == 400
    locked = post(client, verify_url, otp="000000")
    assert locked.status_code == 429 and 'name="otp"' not in locked.text
    assert post(client, verify_url, otp=old).status_code == 429

    world.advance(299)
    assert google(client, world.oidc, login_only=True).status_code == 429
    assert len(world.mail) == 1 and not client.cookies.get("storefront_session")
    world.advance(1)
    replacement = google(client, world.oidc, login_only=True)
    assert replacement.status_code == 200 and len(world.mail) == 2 and world.mail[-1][1] != old
    rejected = post(client, verify_url, otp=old)
    assert rejected.status_code == 400
    assert post(client, verify_url, otp=world.mail[-1][1]).status_code == 303
    assert client.cookies.get("storefront_session")


def test_uc02_ac20_both_portals_in_one_browser(world):
    world.seed_member("customer@example.com")
    world.seed_member("staff@example.com", role="employee", phone="0981234567")
    client = signed_in(world, "customer@example.com")
    signed_in(world, "staff@example.com", portal=True, client=client)
    assert client.cookies.get("storefront_session") != client.cookies.get("portal_session")
    assert client.get("/api/v1/identity/account/profile").status_code == client.get("/api/v1/identity/portal/customers").status_code == 200


@pytest.mark.parametrize("portal", [False, True], ids=["storefront", "portal"])
@pytest.mark.parametrize("htmx", [False, True], ids=["form", "htmx"])
def test_uc02_login_origin_checked_before_session_and_rate_limit(world, portal, htmx):
    email = "member@example.com"
    world.seed_member(email, role="employee" if portal else "customer", phone="0981234567")
    client = world.client
    path = PORTAL_LOGIN if portal else LOGIN
    page = client.get(path)
    assert 'name="csrf_token"' not in page.text
    assert page.headers["referrer-policy"] == "strict-origin"
    headers = {"HX-Request": "true"} if htmx else {}
    invalid = (headers, headers | {"Origin": "null"}, headers | {"Origin": "https://other.example"})
    for _ in range(2):
        for supplied in invalid:
            assert post(client, path, headers=supplied, identifier=email, password="123456").status_code == 403
    assert not world.sql("SELECT 1 FROM identity.session")
    assert post(client, path, headers=headers | {"Origin": "https://testserver"},
                identifier=email, password="123456").status_code == 303
    before = world.sql("SELECT * FROM identity.session")
    world.advance(60)
    for supplied in invalid:
        assert post(client, path, headers=supplied, identifier=email, password="123456").status_code == 403
    assert world.sql("SELECT * FROM identity.session") == before


@pytest.mark.parametrize("branch", ["password", "google", "otp"])
def test_uc02_ac7_checkout_merges_cart_once(world, monkeypatch, branch):
    from app.main import app

    monkeypatch.setitem(app.state._state, "shopping_session_factory", app.state.identity_service.session_factory)
    account = world.seed_member("google@example.com",
                                google_sub="google-sub" if branch == "google" else None, password=branch != "google")
    cart = world.sql("INSERT INTO shopping.cart (cart_account_key) VALUES ($1) RETURNING cart_key", account)[0][0]
    variants = world.sql("""
        SELECT variant_key, variant_id, stock_quantity
        FROM catalog.variant JOIN catalog.product ON product_key = variant_product_key
        JOIN inventory.stock ON stock_variant_key = variant_key
        WHERE variant_status = 'ACTIVE' AND product_status = 'ACTIVE'
          AND variant_sell_price IS NOT NULL AND stock_quantity >= 3
        ORDER BY variant_id LIMIT 2
    """)
    capped, other = variants
    world.sql("""
        INSERT INTO shopping.cart_item (cart_item_cart_key, cart_item_variant_key, cart_item_quantity)
        VALUES ($1, $2, $3)
    """, cart, capped["variant_key"], capped["stock_quantity"] - 1, fetch=False)
    client = world.client
    start = client.get(CHECKOUT, follow_redirects=False)
    assert start.status_code == 303
    entry = urlsplit(start.headers["location"])
    assert entry.path == LOGIN and parse_qs(entry.query) == {"return_to": [CHECKOUT]}
    page = client.get(start.headers["location"])
    if branch == "password":
        action = unescape(re.search(r'<form [^>]*action="([^"]+)"', page.text)[1])
        response = post(client, action, identifier="google@example.com", password="123456")
    else:
        url = unescape(re.search(r'href="([^"]+/register/google\?[^"]+)"', page.text)[1])
        start_google = client.get(url, follow_redirects=False)
        state = parse_qs(urlsplit(start_google.headers["location"]).query)["state"][0]
        response = client.get(f"{PREFIX}/register/google/callback", params={"state": state, "code": "valid"},
                              follow_redirects=False)
        if branch == "otp":
            assert response.status_code == 200 and world.mail
            response = post(client, f"{PREFIX}/register/google/link/otp", otp=world.mail[-1][1])
    assert response.status_code == 303 and response.headers["location"] == CHECKOUT
    assert client.cookies.get("storefront_session")

    data = {"merge_key": str(uuid4()), "variant_key": [str(row["variant_key"]) for row in variants],
            "quantity": ["2", "1"]}
    first = post(client, MERGE, **data)
    replay = post(client, MERGE, **data)
    assert first.status_code == replay.status_code == 200 and first.json() == replay.json()
    assert [(row["added"], row["status"]) for row in first.json()["items"]] == [(1, "limited"), (1, "merged")]
    assert post(client, MERGE, **(data | {"quantity": ["2", "2"]})).status_code == 409
    assert dict(world.sql("""
        SELECT cart_item_variant_key, cart_item_quantity FROM shopping.cart_item WHERE cart_item_cart_key = $1
    """, cart)) == {capped["variant_key"]: capped["stock_quantity"], other["variant_key"]: 1}
    checkout = client.get(CHECKOUT)
    assert checkout.status_code == 200
    assert f'{capped["variant_id"]}) × {capped["stock_quantity"]}' in checkout.text
    assert f'{other["variant_id"]}) × 1' in checkout.text
