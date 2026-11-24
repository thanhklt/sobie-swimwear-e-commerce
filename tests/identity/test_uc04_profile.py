import pytest

from identity_support import login, profile, signed_in, submit
from test_uc01_register_account import post


def test_uc04_ac1_and_ac2_saved_contacts_work_without_reverification(world):
    key = world.seed_member("old@example.com")
    client = signed_in(world, "old@example.com")
    values = profile()
    response = submit(client, "/account/profile", **values)
    assert response.status_code == 303
    page = client.get(response.headers["location"])
    assert all(value in page.text for value in values.values())
    row = world.sql("SELECT account_email, account_phone_number FROM identity.account WHERE account_key=$1", key)
    assert tuple(row[0]) == (values["email"], values["phone_number"])
    assert not world.mail
    assert post(client, page, "/logout").status_code == 303
    for identifier in (values["email"], values["phone_number"]):
        assert login(world.new_client(), identifier).status_code == 303
    assert login(world.new_client(), "old@example.com").status_code == 401


@pytest.mark.parametrize("fields,message", [
    ({"email": "taken@example.com"}, "Email đã được sử dụng"),
    ({"phone_number": "abc"}, "Số điện thoại không hợp lệ"),
    ({"name": ""}, "Vui lòng nhập họ tên"),
])
def test_uc04_ac3_and_ac4_profile_error_preserves_existing_values(world, fields, message):
    key = world.seed_member("old@example.com")
    world.seed_member("taken@example.com")
    response = submit(signed_in(world, "old@example.com"), "/account/profile", **profile(**fields))
    assert response.status_code == 400 and message in response.text
    assert world.sql("SELECT account_email FROM identity.account WHERE account_key=$1", key)[0][0] == "old@example.com"


def test_uc04_ac5_admin_edits_selected_customer(world):
    key = world.seed_member("old@example.com")
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    current_code = world.sql("SELECT account_id FROM identity.account WHERE account_key=$1", key)[0][0]
    admin = signed_in(world, "admin@example.com", portal=True)
    customer = signed_in(world, "old@example.com")
    response = submit(admin, f"/admin/accounts/{key}/edit", **profile(email="old@example.com"))
    assert response.status_code == 303
    page = customer.get("/account/profile")
    assert current_code in page.text and "Nguyễn Minh Anh" in page.text
