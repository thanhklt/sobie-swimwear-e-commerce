import asyncio
import os
from urllib.parse import urlparse

import asyncpg
import pytest

from identity_support import profile, signed_in, submit


@pytest.mark.parametrize("role,prefix", [
    ("employee", "NV-NGUYENMINHANH-19950101-"),
    ("admin", "AD-NGUYENMINHANH-19950101-"),
    ("customer", "KH-20261124-"),
])
def test_uc06_ac1_ac2_ac4_ac6_admin_creates_account(world, role, prefix):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    admin = signed_in(world, "admin@example.com", portal=True)
    path = "/admin/accounts/new"
    page = admin.get(path)
    assert all(f'value="{option}"' in page.text for option in ("customer", "employee", "admin"))
    response = submit(admin, path, **profile(role=role, password="open123"))
    assert response.status_code == 303
    assert "new@example.com" in admin.get(response.headers["location"]).text
    rows = world.sql(
        """SELECT account_id, role_code, account_status,
                  crypt('open123', account_hash_password) = account_hash_password
           FROM identity.account JOIN identity.role ON role_key=account_role_key
           WHERE account_email='new@example.com'"""
    )
    assert rows[0][0].startswith(prefix)
    assert tuple(rows[0])[1:] == (role, "ACTIVE", True)
    assert world.counts()[1:3] == ((1, 1) if role == "customer" else (0, 0))


@pytest.mark.parametrize("fields,message", [
    ({"email": "taken@example.com"}, "Email đã được sử dụng"),
    ({"phone_number": "0901000002"}, "Số điện thoại đã được sử dụng"),
    ({"password": "12345"}, "Mật khẩu phải có ít nhất 6 ký tự"),
    ({"role": "owner"}, "Vai trò không hợp lệ"),
    ({"role": "employee", "date_of_birth": ""}, "Vui lòng nhập ngày sinh"),
])
def test_uc06_ac3_ac6_ac8_invalid_form(world, fields, message):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    world.seed_member("taken@example.com", phone="0901000002")
    admin = signed_in(world, "admin@example.com", portal=True)
    data = profile(role="customer", password="open123") | fields
    response = submit(admin, "/admin/accounts/new", **data)
    assert response.status_code == 400 and message in response.text
    assert world.counts() == (2, 0, 0, 0)


def test_uc06_ac5_employee_cannot_create(world):
    world.seed_member("staff@example.com", role="employee", phone="0981234567")
    staff = signed_in(world, "staff@example.com", portal=True)
    assert staff.get("/admin/accounts/new").status_code == 403
    from test_uc01_register_account import post
    data = profile(role="admin", password="open123")
    assert post(staff, staff.get("/admin/customers"), "/admin/accounts/new", **data).status_code == 403
    assert world.counts() == (1, 0, 0, 0)


@pytest.mark.parametrize("failure", ["suffix", "save_account", "cart", "wishlist"])
def test_uc06_ac7_rollback_includes_code_account_and_shopping(world, failure):
    world.seed_member("admin@example.com", role="admin", phone="0901000001")
    admin = signed_in(world, "admin@example.com", portal=True, client=world.client_without_server_exceptions())
    before = world.counts()
    with world.fail_at(failure):
        assert submit(admin, "/admin/accounts/new", **profile(role="customer", password="open123")).status_code == 500
    assert world.counts() == before


def test_uc06_ac9_active_admin_exists_after_fresh_schema():
    dsn = os.getenv("UC06_BOOTSTRAP_DATABASE_URL")
    if not dsn:
        pytest.skip("Cần PostgreSQL riêng mới nạp init.sql cho UC-06 AC-9")
    assert urlparse(dsn).path == "/uc01bootstrap"

    async def count_admins():
        connection = await asyncpg.connect(dsn)
        try:
            return await connection.fetchval("""SELECT count(*)
                FROM identity.account JOIN identity.role ON account_role_key=role_key
                WHERE role_code='admin' AND account_status='ACTIVE'""")
        finally:
            await connection.close()

    assert asyncio.run(count_admins()) == 1
