from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from identity_support import login, signed_in
from test_uc01_register_account import post


def lock(client, page, key, *, action="lock", confirm="yes"):
    return post(client, client.get(page), f"/admin/accounts/{key}/{action}", confirm=confirm)


def test_uc08_ac1_ac2_ac3_ac4_confirm_cancel_revoke_and_unlock(world):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    key = world.seed_member("customer@example.com")
    admin = signed_in(world, "admin@example.com", portal=True)
    path = f"/admin/accounts/{key}/edit"
    customer = signed_in(world, "customer@example.com")
    copied = customer.cookies["storefront_session"]
    assert lock(admin, path, key, confirm="no").status_code == 303
    assert customer.get("/account/profile").status_code == 200
    response = lock(admin, path, key)
    assert response.status_code == 303 and "Đã khóa tài khoản" in admin.get(response.headers["location"]).text
    assert customer.get("/account/profile", follow_redirects=False).headers["location"] == "/api/v1/login"
    assert login(world.new_client(), "customer@example.com").status_code == 403
    response = lock(admin, path, key, action="unlock")
    assert response.status_code == 303 and "Đã mở khóa tài khoản" in admin.get(response.headers["location"]).text
    customer.cookies.set("storefront_session", copied, domain="testserver.local", path="/")
    assert customer.get("/account/profile", follow_redirects=False).headers["location"] == "/api/v1/login"
    assert login(customer, "customer@example.com").status_code == 303


def test_uc08_ac5_ac7_admin_can_lock_self_only_with_another_active_admin(world):
    key = world.seed_member("admin@example.com", role="admin", phone="0901000001")
    admin = signed_in(world, "admin@example.com", portal=True)
    path = f"/admin/accounts/{key}/edit"
    assert lock(admin, path, key).status_code == 400
    assert admin.get(path).status_code == 200
    world.seed_member("other@example.com", role="admin", phone="0901000002")
    response = lock(admin, path, key)
    assert response.status_code == 303 and response.headers["location"] == "/api/v1/admin/login?locked=1"
    assert login(admin, "admin@example.com", portal=True).status_code == 403


def test_uc08_ac6_ac8_ac9_employee_can_only_lock_customer(world):
    admin_key = world.seed_member("admin@example.com", role="admin", phone="0901000001")
    staff_key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    customer_key = world.seed_member("customer@example.com")
    staff = signed_in(world, "staff@example.com", portal=True)
    page = f"/admin/customers/{customer_key}"
    assert lock(staff, page, admin_key).status_code == 403
    assert lock(staff, page, staff_key).status_code == 403
    assert lock(staff, page, customer_key).status_code == 303
    assert 'Mở khóa tài khoản' not in staff.get(page).text
    assert lock(staff, "/admin/password", customer_key, action="unlock").status_code == 403
    assert login(world.new_client(), "customer@example.com").status_code == 403


def test_uc08_ac10_lock_and_demotion_leave_an_active_admin(world):
    first = world.seed_member("one@example.com", role="admin", phone="0901000001")
    second = world.seed_member("two@example.com", role="admin", phone="0901000002")
    locker = signed_in(world, "one@example.com", portal=True)
    editor = signed_in(world, "two@example.com", portal=True)
    first_page = locker.get(f"/admin/accounts/{first}/edit")
    second_path = f"/admin/accounts/{second}/edit"
    second_page = editor.get(second_path)
    start = Barrier(2, timeout=10)

    def submit_lock():
        start.wait()
        return post(locker, first_page, f"/admin/accounts/{first}/lock", confirm="yes")

    def submit_demote():
        start.wait()
        return post(editor, second_page, second_path, role="employee")

    with ThreadPoolExecutor(max_workers=2) as workers:
        lock_response = workers.submit(submit_lock)
        demote_response = workers.submit(submit_demote)
        assert sorted((lock_response.result().status_code, demote_response.result().status_code)) == [303, 400]
    assert world.sql("""SELECT count(*) FROM identity.account JOIN identity.role
        ON account_role_key=role_key WHERE role_code='admin' AND account_status='ACTIVE'""")[0][0] == 1
