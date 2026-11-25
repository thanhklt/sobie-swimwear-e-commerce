from datetime import date

import pytest

from identity_support import login, post, profile, signed_in, submit


PROFILE_PATH = "/api/v1/identity/account/profile"


def stored_profile(world, key):
    row = world.sql(
        """SELECT account_id, account_name, account_date_of_birth, account_house_number,
                  account_ward, account_city, account_country, account_email, account_phone_number
           FROM identity.account WHERE account_key=$1""",
        key,
    )[0]
    return {column.removeprefix("account_"): value for column, value in row.items()}


def test_uc04_ac1_and_ac2_saved_contacts_work_without_reverification(world):
    key = world.seed_member("old@example.com")
    before = stored_profile(world, key)
    client = signed_in(world, "old@example.com")
    values = profile(date_of_birth="1990-02-03")
    response = submit(client, PROFILE_PATH, **values)
    assert response.status_code == 303
    assert response.headers["location"] == PROFILE_PATH + "?saved=1"
    page = client.get(response.headers["location"])
    assert page.status_code == 200
    assert "Đã lưu thông tin tài khoản" in page.text
    assert all(value in page.text for value in values.values())
    assert stored_profile(world, key) == values | {
        "id": before["id"],
        "date_of_birth": date.fromisoformat(values["date_of_birth"]),
    }
    assert not world.mail
    assert post(client, "/api/v1/identity/logout").status_code == 303
    for identifier in (values["email"], values["phone_number"]):
        assert login(world.new_client(), identifier).status_code == 303
    assert login(world.new_client(), "old@example.com").status_code == 401


@pytest.mark.parametrize("field,value,message", [
    ("email", "taken@example.com", "Email đã được sử dụng"),
    ("phone_number", "abc", "Số điện thoại không hợp lệ"),
    ("name", "", "Vui lòng nhập họ tên"),
])
def test_uc04_ac3_and_ac4_profile_error_preserves_existing_values(world, field, value, message):
    key = world.seed_member("old@example.com", phone="0901000001")
    world.seed_member("taken@example.com")
    before = stored_profile(world, key)
    client = signed_in(world, "old@example.com")
    response = submit(client, PROFILE_PATH, **profile(**{field: value}))
    assert response.status_code == 400
    input_markup, separator, following_markup = response.text.partition(f'id="{field}"')
    assert input_markup and separator
    field_markup = following_markup.split("<label", 1)[0]
    assert f'<p role="alert">{message}</p>' in field_markup
    assert stored_profile(world, key) == before


def test_uc04_ac5_admin_edits_selected_customer(world):
    key = world.seed_member("old@example.com")
    other_key = world.seed_member("other@example.com")
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    before = stored_profile(world, key)
    other_before = stored_profile(world, other_key)
    assert before["id"].startswith("KH-")
    admin = signed_in(world, "admin@example.com", portal=True)
    customer = signed_in(world, "old@example.com")
    updates = {"name": "Nguyễn Minh Anh", "house_number": "12 Nguyễn Huệ"}
    response = submit(admin, f"/api/v1/identity/portal/accounts/{key}/edit", **updates)
    assert response.status_code == 303
    assert stored_profile(world, key) == before | updates
    assert stored_profile(world, other_key) == other_before
    page = customer.get(PROFILE_PATH)
    assert page.status_code == 200
    assert all(value in page.text for value in (before["id"], *updates.values()))
