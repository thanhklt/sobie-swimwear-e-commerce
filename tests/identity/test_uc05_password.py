import pytest

from identity_support import login, signed_in, submit


@pytest.mark.parametrize("portal", [False, True])
def test_uc05_ac1_ac5_ac6_all_sessions_revoked_on_password_change(world, portal):
    world.seed_member("user@example.com", role="employee" if portal else "customer", phone="0981234567")
    client = signed_in(world, "user@example.com", portal=portal)
    other = signed_in(world, "user@example.com", portal=portal)
    form = "/admin/password" if portal else "/account/password"
    login_path = "/api/v1/admin/login" if portal else "/api/v1/login"
    result = submit(client, form, current_password="123456", password="password2", password_confirmation="password2")
    assert result.status_code == 303 and result.headers["location"].startswith(login_path)
    assert "Đổi mật khẩu thành công" in client.get(result.headers["location"]).text
    assert other.get(form, follow_redirects=False).headers["location"] == login_path
    assert login(other, "user@example.com", "password2", portal=portal).status_code == 303
    assert login(world.new_client(), "user@example.com", portal=portal).status_code == 401


@pytest.mark.parametrize("current,password,confirm,message", [
    ("bad", "password2", "password2", "Mật khẩu hiện tại không đúng"),
    ("123456", "bad", "bad", "Mật khẩu phải có ít nhất 6 ký tự"),
    ("123456", "123456", "123456", "Mật khẩu mới phải khác mật khẩu hiện tại"),
    ("123456", "password2", "password3", "Mật khẩu xác nhận không khớp"),
])
def test_uc05_ac2_ac3_ac4_ac7_rejected_change_preserves_sessions(world, current, password, confirm, message):
    world.seed_member("user@example.com")
    client = signed_in(world, "user@example.com")
    response = submit(client, "/account/password", current_password=current, password=password, password_confirmation=confirm)
    assert response.status_code == 400 and message in response.text
    assert client.get("/account/profile").status_code == 200


def test_uc05_ac7_revoke_failure_rolls_back_hash_and_sessions(world):
    world.seed_member("user@example.com")
    client = signed_in(world, "user@example.com", client=world.client_without_server_exceptions())
    other = signed_in(world, "user@example.com")
    with world.fail_at("revoke"):
        response = submit(client, "/account/password", current_password="123456", password="password2",
                          password_confirmation="password2")
    assert response.status_code == 500
    assert other.get("/account/profile").status_code == 200
    assert login(world.new_client(), "user@example.com").status_code == 303
