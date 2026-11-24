import pytest

from identity_support import profile, signed_in, submit
from test_uc01_register_account import post


def seed_admin(world, n=1):
    email = f"admin{n}@example.com"
    key = world.seed_member(email, role="admin", phone=f"090100000{n}")
    return key, email


def test_uc07_ac1_account_list_paginates_25_accounts(world):
    _, email = seed_admin(world)
    for n in range(24):
        world.seed_member(f"customer{n:02}@example.com", phone=f"09023456{n:02}")
    admin = signed_in(world, email, portal=True)
    first = admin.get("/admin/accounts")
    second = admin.get("/admin/accounts?page=2")
    assert first.status_code == second.status_code == 200
    assert first.headers["cache-control"] == second.headers["cache-control"] == "no-store"
    assert first.text.count("<li>") == 20 and second.text.count("<li>") == 5
    assert "Trang sau" in first.text and "Trang trước" in second.text
    assert "customer00@example.com" in first.text and "customer00@example.com" not in second.text
    assert "customer23@example.com" in second.text and "customer23@example.com" not in first.text


@pytest.mark.parametrize("search", ["Sobie Test", "contact", "0981234567"])
def test_uc07_ac2_ac3_list_search(world, search):
    _, email = seed_admin(world)
    world.seed_member("contact@example.com", phone="0981234567")
    admin = signed_in(world, email, portal=True)
    index = admin.get("/admin/accounts")
    assert index.headers["cache-control"] == "no-store"
    assert all(text in index.text for text in ("contact@example.com", "0981234567", "Khách hàng", "Hoạt động"))
    assert "contact@example.com" in admin.get("/admin/accounts", params={"q": search}).text
    assert "Không tìm thấy tài khoản" in admin.get("/admin/accounts", params={"q": "no-match"}).text


def test_uc07_ac4_ac6_edit_fields_and_reject_duplicate(world):
    _, email = seed_admin(world)
    key = world.seed_member("contact@example.com", role="employee", phone="0981234567")
    world.seed_member("duplicate@example.com", role="employee", phone="0981234568")
    admin = signed_in(world, email, portal=True)
    path = f"/admin/accounts/{key}/edit"
    response = submit(admin, path, **profile(email="duplicate@example.com", role="admin"))
    assert response.status_code == 400 and "Email đã được sử dụng" in response.text
    unchanged = world.sql("""SELECT account_email, role_code FROM identity.account
        JOIN identity.role ON account_role_key=role_key WHERE account_key=$1""", key)
    assert tuple(unchanged[0]) == ("contact@example.com", "employee")
    assert submit(admin, path, **profile(role="employee")).status_code == 303
    page = admin.get(path + "?saved=1")
    assert "Nguyễn Minh Anh" in page.text and "Đã lưu thông tin tài khoản" in page.text


def test_uc07_ac5_ac10_promotion_renumbers_and_revokes(world):
    _, email = seed_admin(world)
    key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    staff = signed_in(world, "staff@example.com", portal=True)
    admin = signed_in(world, email, portal=True)
    response = submit(admin, f"/admin/accounts/{key}/edit", role="admin")
    assert response.status_code == 303
    assert staff.get("/admin/customers", follow_redirects=False).headers["location"] == "/api/v1/admin/login"
    rows = world.sql("""SELECT account_id, role_code, account_email, account_phone_number,
          crypt('123456', account_hash_password) = account_hash_password
          FROM identity.account JOIN identity.role ON account_role_key=role_key WHERE account_key=$1""", key)
    assert rows[0][0].startswith("AD-SOBIETEST-19950101-")
    assert tuple(rows[0])[1:] == ("admin", "staff@example.com", "0981234567", True)


def test_uc07_ac4_ac5_ac10_profile_and_role_save_together(world):
    _, email = seed_admin(world)
    key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    staff = signed_in(world, "staff@example.com", portal=True)
    admin = signed_in(world, email, portal=True)
    path = f"/admin/accounts/{key}/edit"
    page = admin.get(path)
    edit_form = page.text.split('<form method="post" class="identity-form">', 1)[1].split("</form>", 1)[0]
    assert 'name="name"' in edit_form and 'name="role"' in edit_form and ">Lưu</button>" in edit_form
    response = post(admin, page, path, **profile(role="admin", date_of_birth="1999-01-05"))
    assert response.status_code == 303
    rows = world.sql("""SELECT account_id, role_code, account_name, account_email, account_phone_number
        FROM identity.account JOIN identity.role ON account_role_key=role_key WHERE account_key=$1""", key)
    assert rows[0][0].startswith("AD-NGUYENMINHANH-19990105-")
    assert tuple(rows[0])[1:] == ("admin", "Nguyễn Minh Anh", "new@example.com", "0912345678")
    assert staff.get("/admin", follow_redirects=False).headers["location"] == "/api/v1/admin/login"


@pytest.mark.parametrize("before,after", [("customer", "admin"), ("employee", "customer"), ("admin", "customer")])
def test_uc07_ac7_ac8_no_transition_between_customer_and_staff(world, before, after):
    _, email = seed_admin(world)
    key = world.seed_member("target@example.com", role=before, phone="0981234567")
    admin = signed_in(world, email, portal=True)
    path = f"/admin/accounts/{key}/edit"
    if before == "customer":
        assert 'name="role"' not in admin.get(path).text
    assert submit(admin, path, role=after).status_code == 400
    assert world.sql("""SELECT role_code FROM identity.account JOIN identity.role
                        ON account_role_key=role_key WHERE account_key=$1""", key)[0][0] == before


def test_uc07_ac9_ac14_ac15_employee_customer_access_only(world):
    admin_key, _ = seed_admin(world)
    staff_key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    customer_key = world.seed_member("customer@example.com")
    staff = signed_in(world, "staff@example.com", portal=True)
    page = staff.get("/admin/customers")
    assert "customer@example.com" in page.text and "admin1@example.com" not in page.text
    assert staff.get(f"/admin/customers/{customer_key}").status_code == 200
    assert staff.get("/admin/accounts").status_code == 403
    assert staff.get(f"/admin/customers/{admin_key}").status_code == 404
    assert staff.get(f"/admin/customers/{staff_key}").status_code == 404
    assert post(staff, page, f"/admin/accounts/{customer_key}/edit", **profile()).status_code == 403


def test_uc07_ac11_ac13_self_demotion_requires_another_admin(world):
    key, email = seed_admin(world)
    admin = signed_in(world, email, portal=True)
    path = f"/admin/accounts/{key}/edit"
    assert submit(admin, path, role="employee").status_code == 400
    assert admin.get(path).status_code == 200
    seed_admin(world, 2)
    response = submit(admin, path, role="employee")
    assert response.status_code == 303 and response.headers["location"] == "/api/v1/admin/login?role_changed=1"
    assert not admin.cookies.get("portal_session")


def test_uc07_ac12_failure_keeps_existing_role_code_and_sessions(world):
    _, email = seed_admin(world)
    key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    staff = signed_in(world, "staff@example.com", portal=True)
    admin = signed_in(world, email, portal=True, client=world.client_without_server_exceptions())
    query = """SELECT account_id, account_role_key, account_name, account_email, account_phone_number
        FROM identity.account WHERE account_key=$1"""
    counter_query = "SELECT last_number FROM identity.account_id_counter WHERE account_prefix='AD'"
    before = world.sql(query, key)
    counter_before = world.sql(counter_query)
    with world.fail_at("save_account"):
        response = submit(admin, f"/admin/accounts/{key}/edit", **profile(role="admin"))
    assert response.status_code == 500
    assert world.sql(query, key) == before
    assert world.sql(counter_query) == counter_before
    assert staff.get("/admin/customers").status_code == 200
