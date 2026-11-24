import pytest

from identity_support import login, signed_in
from test_uc01_register_account import google, post


@pytest.mark.parametrize("role, portal, by_phone", [
    ("customer", False, False), ("customer", False, True),
    ("employee", True, False), ("admin", True, False),
])
def test_uc02_ac1_ac2_ac3_password_login(world, role, portal, by_phone):
    world.seed_member("member@example.com", role=role, phone="0981234567")
    client = world.new_client()
    response = login(client, "0981234567" if by_phone else "MEMBER@example.com", portal=portal)
    assert response.status_code == 303 and response.headers["location"] == ("/admin" if portal else "/")
    cookie = "portal_session" if portal else "storefront_session"
    header = response.headers.get_list("set-cookie")
    assert any(cookie + "=" in entry and all(flag in entry.lower() for flag in ("secure", "httponly", "samesite=lax"))
               for entry in header)
    rows = world.sql("SELECT session_expires_at - session_created_at AS lifetime FROM identity.session")
    assert rows[0]["lifetime"].total_seconds() == (3600 if portal else 1800)

    if portal:
        existing = client.get("/api/v1/admin/login", follow_redirects=False)
        assert existing.status_code == 303 and existing.headers["location"] == "/admin"
        overview = client.get(response.headers["location"])
        title, link = (
            ("Tổng quan Admin", "/admin/accounts")
            if role == "admin" else ("Tổng quan Nhân viên", "/admin/customers")
        )
        assert overview.status_code == 200 and overview.headers["cache-control"] == "no-store"
        assert title in overview.text and f'href="{link}"' in overview.text
        assert overview.url.path == "/admin"


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
    assert 'type="button">Quên mật khẩu' in world.client.get("/api/v1/login").text
    assert "Quên mật khẩu" not in world.client.get("/api/v1/admin/login").text


def test_uc02_ac11_ac12_idle_expiry_and_renewal(world):
    world.seed_member("member@example.com")
    client = signed_in(world, "member@example.com")
    world.advance(1799)
    assert client.get("/account/profile").status_code == 200
    world.advance(1799)
    assert client.get("/account/profile").status_code == 200
    world.advance(1800)
    response = client.get("/account/profile", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/api/v1/login"


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
        response = post(world.client, response, "/register/google/link/otp", otp=code)
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


def test_uc02_ac20_both_portals_in_one_browser(world):
    world.seed_member("customer@example.com")
    world.seed_member("staff@example.com", role="employee", phone="0981234567")
    client = signed_in(world, "customer@example.com")
    signed_in(world, "staff@example.com", portal=True, client=client)
    assert client.cookies.get("storefront_session") != client.cookies.get("portal_session")
    assert client.get("/account/profile").status_code == client.get("/admin/customers").status_code == 200
