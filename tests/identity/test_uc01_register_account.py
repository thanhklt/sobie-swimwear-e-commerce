"""HTTP acceptance checks for UC-01; network providers are replaced at boundaries."""

import re
from urllib.parse import parse_qs, urlparse

import pytest

from identity_support import GOOGLE_CALLBACK, google, post


PREFIX = "/api/v1/identity"
REGISTRATION_POSTS = (
    "/register/email", "/register/otp/resend", "/register/otp",
    "/register/password", "/register/google/link/otp",
)


def begin(client, email="a@example.com"):
    client.get(f"{PREFIX}/register")
    return post(client, f"{PREFIX}/register/email", email=email)


def verify(client, mail, email="a@example.com"):
    begin(client, email)
    return post(client, f"{PREFIX}/register/otp", otp=mail[-1][1])


@pytest.mark.parametrize("path", REGISTRATION_POSTS)
@pytest.mark.parametrize("headers", [
    {"Origin": "https://different.example"},
    {"Origin": "null"},
    {},
], ids=["foreign", "null", "missing"])
def test_uc01_rejects_invalid_origins(world, path, headers):
    client = world.client
    client.get(f"{PREFIX}/register")
    before = world.counts()
    response = post(client, PREFIX + path, headers=headers, email="a@example.com", otp="100000")
    assert response.status_code == 403
    assert not world.mail and world.counts() == before


@pytest.mark.parametrize("headers", [
    {"Origin": "https://testserver"},
    {"Origin": "https://tunnel.example", "X-Forwarded-Proto": "https", "X-Forwarded-Host": "tunnel.example"},
    {"Origin": "https://another.example"},
], ids=["same", "proxy", "allowlist"])
def test_uc01_accepts_allowed_origins(world, monkeypatch, headers):
    from app.config.settings import Config

    monkeypatch.setattr(Config, "ALLOWED_ORIGINS", "https://spare.example, https://another.example")
    client = world.client
    registration = client.get(f"{PREFIX}/register")
    assert registration.status_code == 200 and 'name="csrf_token"' not in registration.text
    assert registration.headers["referrer-policy"] == "strict-origin"
    path = f"{PREFIX}/register/email"
    if "X-Forwarded-Proto" in headers:
        # The proxy terminates HTTPS and forwards the browser's cookie over HTTP.
        cookie_name = "__Host-sobie-registration"
        headers = {**headers, "Cookie": f"{cookie_name}={client.cookies[cookie_name]}"}
        path = "http://testserver" + path
    response = post(client, path, headers=headers, email="a@example.com")
    assert response.status_code == 200 and 'name="otp"' in response.text
    assert 'name="csrf_token"' not in response.text
    assert len(world.mail) == 1 and world.mail[0][0] == "a@example.com"


# UC-01 AC-1: Tạo mật khẩu và hoàn tất đăng ký qua email
def test_uc01_ac1_email_registration(world):
    client, mail = world.client, world.mail
    verify(client, mail)
    result = post(client, f"{PREFIX}/register/password", password="123456", password_confirmation="123456")
    assert result.status_code in (302, 303) and urlparse(result.headers["location"]).path == "/api/v1/identity/login"
    world.assert_new_account("a@example.com", password="123456")
    assert "thành công" in client.get(result.headers["location"]).text.lower()


# UC-01 AC-2: Email đã tồn tại
def test_uc01_ac2_existing_email(world):
    world.seed_account("a@example.com")
    response = begin(world.client)
    assert "Email đã được sử dụng" in response.text
    assert not world.mail and world.counts()[:3] == (1, 1, 1)


# UC-01 AC-4: Email không hợp lệ
@pytest.mark.parametrize("email", ["", "not-an-email"])
def test_uc01_ac4_invalid_email(world, email):
    response = begin(world.client, email)
    assert 'id="email-error"' in response.text
    assert not world.mail and world.counts()[0] == 0


# UC-01 AC-5: Người đã đăng nhập không đăng ký được
def test_uc01_ac5_authenticated_redirect(world):
    world.authenticated()
    response = world.client.get("/api/v1/identity/register", follow_redirects=False)
    assert response.status_code in (302, 303, 307) and response.headers["location"] == "/"


# UC-01 AC-6: Lỗi giữa chừng không để lại dữ liệu dở dang
@pytest.mark.parametrize("failure", ["suffix", "account", "cart", "wishlist"])
def test_uc01_ac6_atomic_registration(world, failure):
    verify(world.client, world.mail)
    before = world.counts()
    with world.fail_at(failure):
        response = post(world.client, f"{PREFIX}/register/password", password="123456", password_confirmation="123456")
    assert "không thành công" in response.text.lower()
    assert world.counts() == before
    response = post(world.client, f"{PREFIX}/register/password", password="123456", password_confirmation="123456")
    assert response.status_code in (302, 303)
    world.assert_new_account("a@example.com", password="123456", suffix="0001")


# UC-01 AC-6: Hoàn tác tài khoản Google cùng liên kết sub
@pytest.mark.parametrize("failure", ["account", "cart", "wishlist"])
def test_uc01_ac6_atomic_google_registration(world, failure):
    before = world.counts()
    with world.fail_at(failure):
        response = google(world.client, world.oidc)
    assert "không thành công" in response.text.lower()
    assert world.counts() == before
    response = google(world.client, world.oidc)
    assert response.status_code in (302, 303)
    world.assert_new_account("google@example.com", google_sub="google-sub", suffix="0001")


# UC-01 AC-7: OTP sai hoặc hết hạn
@pytest.mark.parametrize("kind", ["wrong", "other_email", "expired"])
def test_uc01_ac7_invalid_otp(world, kind):
    begin(world.client)
    otp = world.mail[-1][1]
    if kind == "wrong":
        otp = "wrong"
    elif kind == "other_email":
        other = world.new_client()
        begin(other, "other@example.com")
        otp = world.mail[-1][1]
        assert otp != world.mail[0][1]
    else:
        world.advance(300)
    response = post(world.client, f"{PREFIX}/register/otp", otp=otp)
    assert '/api/v1/identity/register/otp' in response.text and '/api/v1/identity/register/password' not in response.text
    assert world.counts()[0] == 0


# UC-01 AC-8: Từ chối gửi lại OTP trước 5 phút
def test_uc01_ac8_early_resend(world):
    begin(world.client)
    world.advance(299)
    response = post(world.client, f"{PREFIX}/register/otp/resend")
    assert '/api/v1/identity/register/otp' in response.text and len(world.mail) == 1


def test_uc01_ac17_otp_locks_for_five_minutes_after_fifth_failure(world):
    client = world.client
    begin(client)
    old = world.mail[-1][1]
    verify_url = "/api/v1/identity/register/otp"
    resend_url = "/api/v1/identity/register/otp/resend"
    world.advance(30)
    for _ in range(4):
        page = post(client, verify_url, otp="000000")
        assert page.status_code == 400 and 'name="otp"' in page.text
    page = post(client, verify_url, otp="000000")
    assert page.status_code == 429 and 'name="otp"' not in page.text
    assert 'name="otp"' not in client.get("/api/v1/identity/register").text
    assert post(client, verify_url, otp=old).status_code == 429

    world.advance(299)
    assert post(client, resend_url).status_code == 429
    assert begin(world.new_client()).status_code == 400
    assert len(world.mail) == 1
    world.advance(1)
    assert post(client, verify_url, otp=old).status_code == 429
    page = post(client, resend_url)
    assert page.status_code == 200 and len(world.mail) == 2 and world.mail[-1][1] != old
    page = post(client, verify_url, otp=old)
    assert page.status_code == 400
    result = post(client, verify_url, otp=world.mail[-1][1])
    assert result.status_code == 200 and '/api/v1/identity/register/password' in result.text


# UC-01 AC-11: Gửi lại OTP khi đã đủ 5 phút
def test_uc01_ac11_resend_at_expiry(world):
    begin(world.client)
    old = world.mail[-1][1]
    world.advance(300)
    post(world.client, f"{PREFIX}/register/otp/resend")
    assert len(world.mail) == 2 and world.mail[-1][0] == "a@example.com"
    assert world.mail[-1][1] != old
    rejected = post(world.client, f"{PREFIX}/register/otp", otp=old)
    assert '/api/v1/identity/register/password' not in rejected.text
    world.advance(299)
    accepted = post(world.client, f"{PREFIX}/register/otp", otp=world.mail[-1][1])
    assert '/api/v1/identity/register/password' in accepted.text


# UC-01 AC-11: OTP mới hết hạn sau 5 phút từ lần gửi lại
def test_uc01_ac11_resent_code_expires(world):
    begin(world.client)
    world.advance(300)
    post(world.client, f"{PREFIX}/register/otp/resend")
    code = world.mail[-1][1]
    world.advance(300)
    response = post(world.client, f"{PREFIX}/register/otp", otp=code)
    assert '/api/v1/identity/register/password' not in response.text
    assert world.counts()[0] == 0


# UC-01 AC-12: Xác minh OTP thành công
def test_uc01_ac12_verified_email(world):
    page = verify(world.client, world.mail)
    assert '/api/v1/identity/register/password' in page.text and world.counts()[0] == 0


# UC-01 AC-13: Mật khẩu không hợp lệ
@pytest.mark.parametrize("password,confirmation", [("", "123456"), ("123456", ""), ("12345", "12345"), ("123456", "654321")])
def test_uc01_ac13_invalid_password(world, password, confirmation):
    verify(world.client, world.mail)
    response = post(world.client, f"{PREFIX}/register/password", password=password, password_confirmation=confirmation)
    assert '/api/v1/identity/register/password' in response.text and world.counts()[0] == 0


# UC-01 AC-14: Đăng ký thành công bằng Google
def test_uc01_ac14_new_google_account(world):
    response = google(world.client, world.oidc)
    assert response.status_code in (302, 303) and urlparse(response.headers["location"]).path == "/api/v1/identity/login"
    world.assert_new_account("google@example.com", google_sub="google-sub")
    assert not world.client.cookies.get("storefront_session")
    assert "Đăng ký thành công" in world.client.get(response.headers["location"]).text


def test_uc01_ac14_registration_state_survives_another_google_attempt(world):
    client = world.client
    registration = client.get("/api/v1/identity/register")
    href = re.search(r'href="([^"]+)">Đăng ký với Google</a>', registration.text)
    assert href
    signup = client.get(href.group(1), follow_redirects=False)
    signin = client.get("/api/v1/identity/register/google", params={"login": "1"}, follow_redirects=False)
    signup_state = parse_qs(urlparse(signup.headers["location"]).query)["state"][0]
    signin_state = parse_qs(urlparse(signin.headers["location"]).query)["state"][0]
    assert signup_state != signin_state

    callback = GOOGLE_CALLBACK
    result = client.get(callback, params={"state": signup_state, "code": "signup"}, follow_redirects=False)
    assert result.status_code == 303 and urlparse(result.headers["location"]).path == "/api/v1/identity/login"
    world.assert_new_account("google@example.com", google_sub="google-sub")
    assert not client.cookies.get("storefront_session")
    assert "Đăng ký thành công" in client.get(result.headers["location"]).text

    # Callback của lượt đăng ký chỉ được xử lý một lần.
    replay = client.get(callback, params={"state": signup_state, "code": "signup"}, follow_redirects=False)
    assert replay.status_code == 400 and not client.cookies.get("storefront_session")
    signin_result = client.get(callback, params={"state": signin_state, "code": "signin"}, follow_redirects=False)
    assert signin_result.status_code == 303 and signin_result.headers["location"] == "/"
    assert world.counts()[:3] == (1, 1, 1)


# UC-01 AC-15: Xác thực Google chưa thành công
@pytest.mark.parametrize("failure", ["cancel", "invalid", "unverified"])
def test_uc01_ac15_failed_google_verification(world, failure):
    world.oidc.failure = failure
    assert google(world.client, world.oidc).status_code == 400
    assert world.counts()[0] == 0


# UC-01 AC-16: Dùng Google khi đã có tài khoản Sobie
@pytest.mark.parametrize("linked", [True, False])
def test_uc01_ac16_existing_google_account(world, linked):
    account = world.seed_account("google@example.com", google_sub="google-sub" if linked else None)
    before = world.counts()
    response = google(world.client, world.oidc)
    if not linked:
        assert world.mail[-1][0] == "google@example.com"
        assert not world.client.cookies.get("storefront_session")
        response = post(world.client, f"{PREFIX}/register/google/link/otp", otp=world.mail[-1][1])
    assert response.status_code in (302, 303) and response.headers["location"] == "/"
    assert world.session_account() == account and world.counts() == before
    assert world.google_sub(account) == "google-sub"
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" in cookie and "samesite=" in cookie
    assert world.session_lifetime() == 1800


# UC-01 AC-16: Lỗi cấp phiên hoàn tác liên kết Google vừa tạo
def test_uc01_ac16_google_link_session_rollback(world):
    account = world.seed_account("google@example.com")
    before = world.counts()
    google(world.client, world.oidc)
    with world.fail_at("session"):
        response = post(world.client, f"{PREFIX}/register/google/link/otp", otp=world.mail[-1][1])
    assert response.status_code >= 400
    assert world.google_sub(account) is None
    assert world.counts() == before
    assert not world.client.cookies.get("storefront_session")
