"""Gửi biểu mẫu Identity qua HTTP trong các ca nghiệm thu."""
from test_uc01_register_account import post


def login(client, identifier, password="123456", *, portal=False):
    path = "/api/v1/admin/login" if portal else "/api/v1/login"
    page = client.get(path, follow_redirects=False)
    return post(client, page, path, identifier=identifier, password=password)


def signed_in(world, email, *, portal=False, client=None):
    client = client or world.new_client()
    response = login(client, email, portal=portal)
    assert response.status_code == 303, response.text
    return client


def submit(client, path, **form):
    return post(client, client.get(path), path, **form)


def profile(**updates):
    return {
        "name": "Nguyễn Minh Anh",
        "date_of_birth": "1995-01-01",
        "house_number": "12 Nguyễn Huệ",
        "ward": "Sài Gòn",
        "city": "TP. Hồ Chí Minh",
        "country": "Việt Nam",
        "phone_number": "0912345678",
        "email": "new@example.com",
    } | updates
