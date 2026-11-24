from identity_support import signed_in
from test_uc01_register_account import post


def test_uc03_ac1_ac2_ac4_logout_revokes_only_current_session(world):
    world.seed_member("customer@example.com")
    world.seed_member("staff@example.com", role="employee", phone="0981234567")
    client = signed_in(world, "customer@example.com")
    other = signed_in(world, "customer@example.com")
    signed_in(world, "staff@example.com", portal=True, client=client)
    copied = client.cookies["storefront_session"]
    response = post(client, client.get("/account/profile"), "/logout")
    assert response.status_code == 303 and response.headers["location"] == "/"
    assert not client.cookies.get("storefront_session")
    assert client.get("/account/profile", follow_redirects=False).headers["location"] == "/api/v1/login"
    assert other.get("/account/profile").status_code == 200
    overview = client.get("/admin")
    assert overview.status_code == 200 and "Tổng quan Nhân viên" in overview.text
    portal_logout = post(client, overview, "/admin/logout")
    assert portal_logout.status_code == 303 and portal_logout.headers["location"] == "/"
    assert client.get("/admin", follow_redirects=False).headers["location"] == "/api/v1/admin/login"
    copied_client = world.new_client()
    copied_client.cookies.set("storefront_session", copied)
    assert copied_client.get("/account/profile", follow_redirects=False).headers["location"] == "/api/v1/login"


def test_uc03_ac3_logout_expired_session_is_idempotent(world):
    world.seed_member("customer@example.com")
    client = signed_in(world, "customer@example.com")
    page = client.get("/account/profile")
    world.advance(1800)
    response = post(client, page, "/logout")
    assert response.status_code == 303 and response.headers["location"] == "/"
    assert not client.cookies.get("storefront_session")
