"""HTTP acceptance checks for UC-01; network providers are replaced at boundaries."""

import re
from urllib.parse import parse_qs, urlparse

import pytest


def csrf(response):
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
    assert match, response.text
    return match.group(1)


def post(client, response, path, **data):
    return client.post(path, data={"csrf_token": csrf(response), **data}, follow_redirects=False)


def begin(client, email="a@example.com"):
    return post(client, client.get("/register"), "/register/email", email=email)


def verify(client, mail, email="a@example.com"):
    page = begin(client, email)
    return post(client, page, "/register/otp", otp=mail[-1][1])


def google(client, oidc):
    response = client.get("/register/google", follow_redirects=False)
    assert response.status_code in (302, 303), response.text
    state = parse_qs(urlparse(response.headers["location"]).query)["state"][0]
    params = {"state": state, "error": "access_denied"} if oidc.failure == "cancel" else {"state": state, "code": "valid"}
    return client.get("/register/google/callback", params=params, follow_redirects=False)


# UC-01 AC-1: Tạo mật khẩu và hoàn tất đăng ký qua email
def test_uc01_ac1_email_registration(world):
    client, mail = world.client, world.mail
    page = verify(client, mail)
    result = post(client, page, "/register/password", password="123456", password_confirmation="123456")
    assert result.status_code in (302, 303) and urlparse(result.headers["location"]).path == "/login"
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
    response = world.client.get("/register", follow_redirects=False)
    assert response.status_code in (302, 303, 307) and response.headers["location"] == "/"


# UC-01 AC-6: Lỗi giữa chừng không để lại dữ liệu dở dang
@pytest.mark.parametrize("failure", ["suffix", "account", "cart", "wishlist"])
def test_uc01_ac6_atomic_registration(world, failure):
    page = verify(world.client, world.mail)
    before = world.counts()
    with world.fail_at(failure):
        response = post(world.client, page, "/register/password", password="123456", password_confirmation="123456")
    assert "không thành công" in response.text.lower()
    assert world.counts() == before
    response = post(world.client, page, "/register/password", password="123456", password_confirmation="123456")
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
    page = begin(world.client)
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
    response = post(world.client, page, "/register/otp", otp=otp)
    assert '/register/otp' in response.text and '/register/password' not in response.text
    assert world.counts()[0] == 0


# UC-01 AC-8: Từ chối gửi lại OTP trước 5 phút
def test_uc01_ac8_early_resend(world):
    page = begin(world.client)
    world.advance(299)
    response = post(world.client, page, "/register/otp/resend")
    assert '/register/otp' in response.text and len(world.mail) == 1


# UC-01 AC-11: Gửi lại OTP khi đã đủ 5 phút
def test_uc01_ac11_resend_at_expiry(world):
    page = begin(world.client)
    old = world.mail[-1][1]
    world.advance(300)
    page = post(world.client, page, "/register/otp/resend")
    assert len(world.mail) == 2 and world.mail[-1][0] == "a@example.com"
    assert world.mail[-1][1] != old
    rejected = post(world.client, page, "/register/otp", otp=old)
    assert '/register/password' not in rejected.text
    world.advance(299)
    accepted = post(world.client, rejected, "/register/otp", otp=world.mail[-1][1])
    assert '/register/password' in accepted.text


# UC-01 AC-11: OTP mới hết hạn sau 5 phút từ lần gửi lại
def test_uc01_ac11_resent_code_expires(world):
    page = begin(world.client)
    world.advance(300)
    page = post(world.client, page, "/register/otp/resend")
    code = world.mail[-1][1]
    world.advance(300)
    response = post(world.client, page, "/register/otp", otp=code)
    assert '/register/password' not in response.text
    assert world.counts()[0] == 0


# UC-01 AC-12: Xác minh OTP thành công
def test_uc01_ac12_verified_email(world):
    page = verify(world.client, world.mail)
    assert '/register/password' in page.text and world.counts()[0] == 0


# UC-01 AC-13: Mật khẩu không hợp lệ
@pytest.mark.parametrize("password,confirmation", [("", "123456"), ("123456", ""), ("12345", "12345"), ("123456", "654321")])
def test_uc01_ac13_invalid_password(world, password, confirmation):
    page = verify(world.client, world.mail)
    response = post(world.client, page, "/register/password", password=password, password_confirmation=confirmation)
    assert '/register/password' in response.text and world.counts()[0] == 0


# UC-01 AC-14: Đăng ký thành công bằng Google
def test_uc01_ac14_new_google_account(world):
    response = google(world.client, world.oidc)
    assert response.status_code in (302, 303) and urlparse(response.headers["location"]).path == "/login"
    world.assert_new_account("google@example.com", google_sub="google-sub")


# UC-01 AC-15: Xác thực Google chưa thành công
@pytest.mark.parametrize("failure", ["cancel", "invalid", "unverified"])
def test_uc01_ac15_failed_google_verification(world, failure):
    world.oidc.failure = failure
    google(world.client, world.oidc)
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
        response = post(world.client, response, "/register/google/link/otp", otp=world.mail[-1][1])
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
    page = google(world.client, world.oidc)
    with world.fail_at("session"):
        response = post(world.client, page, "/register/google/link/otp", otp=world.mail[-1][1])
    assert response.status_code >= 400
    assert world.google_sub(account) is None
    assert world.counts() == before
    assert not world.client.cookies.get("storefront_session")
