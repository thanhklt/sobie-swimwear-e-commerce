from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from urllib.parse import parse_qs, urlparse

from identity_support import login, post_with_csrf, signed_in


PORTAL = "/api/v1/identity/portal"


def lock(client, source_page, key, *, action="lock", confirm="yes", **fields):
    path = f"{PORTAL}/accounts/{key}/{action}"
    return post_with_csrf(client, client.get(source_page, follow_redirects=False), path, confirm=confirm, **fields)


def test_uc08_ac1_ac3_ac4_confirm_cancel_revoke_and_unlock(world):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    key = world.seed_member("customer@example.com")
    admin = signed_in(world, "admin@example.com", portal=True)
    path = f"/api/v1/identity/portal/accounts/{key}/edit"
    customer = signed_in(world, "customer@example.com")
    copied = customer.cookies["storefront_session"]
    profile_query = "SELECT account_name, account_email, account_date_of_birth FROM identity.account WHERE account_key = $1"
    original_profile = world.sql(profile_query, key)
    assert lock(admin, path, key, confirm="no").status_code == 303
    assert customer.get("/api/v1/identity/account/profile").status_code == 200
    assert f'action="{PORTAL}/accounts/{key}/lock"' in admin.get(path).text
    response = lock(admin, path, key)
    assert response.status_code == 303 and "Đã khóa tài khoản" in admin.get(response.headers["location"]).text
    assert f'action="{PORTAL}/accounts/{key}/unlock"' in admin.get(path).text
    assert customer.get("/api/v1/identity/account/profile", follow_redirects=False).headers["location"] == "/api/v1/identity/login"
    assert login(world.new_client(), "customer@example.com").status_code == 403
    response = lock(admin, path, key, action="unlock")
    assert response.status_code == 303 and "Đã mở khóa tài khoản" in admin.get(response.headers["location"]).text
    customer.cookies.set("storefront_session", copied, domain="testserver.local", path="/")
    assert customer.get("/api/v1/identity/account/profile", follow_redirects=False).headers["location"] == "/api/v1/identity/login"
    assert login(customer, "customer@example.com").status_code == 303
    assert world.sql(profile_query, key) == original_profile


def test_uc08_ac1_ac3_ac4_admin_toggles_status_from_account_list(world):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    key = world.seed_member("customer@example.com")
    admin = signed_in(world, "admin@example.com", portal=True)
    page = f"{PORTAL}/accounts?q=customer%40example.com&page=1"
    lock_path = f"{PORTAL}/accounts/{key}/lock"
    unlock_path = f"{PORTAL}/accounts/{key}/unlock"
    fields = {"source": "accounts", "q": "customer@example.com", "page": "1"}

    listing = admin.get(page)
    assert f'action="{lock_path}"' in listing.text
    assert 'name="source" value="accounts"' in listing.text
    assert 'type="hidden" name="q" value="customer@example.com"' in listing.text
    assert 'type="hidden" name="page" value="1"' in listing.text
    cancelled = lock(admin, page, key, confirm="no", **fields)
    assert cancelled.status_code == 303
    assert cancelled.headers["location"] == page
    assert f'action="{lock_path}"' in admin.get(page).text

    locked = lock(admin, page, key, **fields)
    assert locked.status_code == 303
    destination = urlparse(locked.headers["location"])
    assert destination.path == f"{PORTAL}/accounts"
    assert parse_qs(destination.query) == {"q": ["customer@example.com"], "page": ["1"], "lock": ["locked"]}
    listing = admin.get(locked.headers["location"])
    assert listing.text.count("Đã khóa tài khoản") == 1
    assert f'action="{unlock_path}"' in listing.text

    unlocked = lock(admin, page, key, action="unlock", **fields)
    assert unlocked.status_code == 303
    assert unlocked.headers["location"] == f"{page}&lock=unlocked"
    listing = admin.get(unlocked.headers["location"])
    assert listing.text.count("Đã mở khóa tài khoản") == 1
    assert f'action="{lock_path}"' in listing.text


def test_uc08_ac2_admin_lock_revokes_employee_portal_session(world):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    employee_key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    admin = signed_in(world, "admin@example.com", portal=True)
    employee = signed_in(world, "staff@example.com", portal=True)
    assert employee.get(f"{PORTAL}/customers").status_code == 200

    response = lock(admin, f"{PORTAL}/accounts/{employee_key}/edit", employee_key)
    assert response.status_code == 303
    revoked = employee.get(f"{PORTAL}/customers", follow_redirects=False)
    assert revoked.status_code == 303 and revoked.headers["location"] == f"{PORTAL}/login"


def test_uc08_ac5_ac7_admin_can_lock_self_only_with_another_active_admin(world):
    key = world.seed_member("admin@example.com", role="admin", phone="0901000001")
    admin = signed_in(world, "admin@example.com", portal=True)
    path = f"/api/v1/identity/portal/accounts/{key}/edit"
    assert lock(admin, path, key).status_code == 400
    assert admin.get(path).status_code == 200
    rejected = lock(admin, f"{PORTAL}/accounts", key, source="accounts", page="1")
    assert rejected.status_code == 400
    assert "Hệ thống phải còn ít nhất một Admin đang hoạt động" in rejected.text
    assert admin.get(f"{PORTAL}/accounts").status_code == 200
    world.seed_member("other@example.com", role="admin", phone="0901000002")
    response = lock(admin, path, key)
    assert response.status_code == 303 and response.headers["location"] == "/api/v1/identity/portal/login?locked=1"
    assert login(admin, "admin@example.com", portal=True).status_code == 403
    other = signed_in(world, "other@example.com", portal=True)
    assert lock(other, path, key, action="unlock").status_code == 303
    assert login(admin, "admin@example.com", portal=True).status_code == 303


def test_uc08_ac6_ac8_ac9_employee_can_only_lock_customer(world):
    admin_key = world.seed_member("admin@example.com", role="admin", phone="0901000001")
    staff_key = world.seed_member("staff@example.com", role="employee", phone="0981234567")
    customer_key = world.seed_member("customer@example.com")
    staff = signed_in(world, "staff@example.com", portal=True)
    page = f"/api/v1/identity/portal/customers/{customer_key}"
    customers = [signed_in(world, "customer@example.com") for _ in range(2)]
    assert all(client.get("/api/v1/identity/account/profile").status_code == 200 for client in customers)
    assert lock(staff, page, admin_key).status_code == 403
    assert lock(staff, page, staff_key).status_code == 403
    assert lock(staff, page, customer_key).status_code == 303
    for customer in customers:
        revoked = customer.get("/api/v1/identity/account/profile", follow_redirects=False)
        assert revoked.status_code == 303 and revoked.headers["location"] == "/api/v1/identity/login"
    assert 'Mở khóa tài khoản' not in staff.get(page).text
    assert lock(staff, "/api/v1/identity/portal/password", customer_key, action="unlock").status_code == 403
    assert login(world.new_client(), "customer@example.com").status_code == 403


def test_uc08_ac10_lock_and_demotion_leave_an_active_admin(world):
    first = world.seed_member("one@example.com", role="admin", phone="0901000001")
    second = world.seed_member("two@example.com", role="admin", phone="0901000002")
    locker = signed_in(world, "one@example.com", portal=True)
    editor = signed_in(world, "two@example.com", portal=True)
    first_page = locker.get(f"/api/v1/identity/portal/accounts/{first}/edit")
    second_path = f"/api/v1/identity/portal/accounts/{second}/edit"
    second_page = editor.get(second_path)
    start = Barrier(2, timeout=10)

    def submit_lock():
        start.wait()
        path = f"/api/v1/identity/portal/accounts/{first}/lock"
        return post_with_csrf(locker, first_page, path, confirm="yes")

    def submit_demote():
        start.wait()
        return post_with_csrf(editor, second_page, second_path, role="employee")

    with ThreadPoolExecutor(max_workers=2) as workers:
        lock_response = workers.submit(submit_lock)
        demote_response = workers.submit(submit_demote)
        assert sorted((lock_response.result().status_code, demote_response.result().status_code)) == [303, 400]
    assert world.sql("""SELECT count(*) FROM identity.account JOIN identity.role
        ON account_role_key=role_key WHERE role_code='admin' AND account_status='ACTIVE'""")[0][0] == 1
