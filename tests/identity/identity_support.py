"""Gửi biểu mẫu Identity qua HTTP trong các ca nghiệm thu."""
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse


GOOGLE_CALLBACK = "/api/v1/identity/register/google/callback"


def post(client, path, *, headers=None, **data):
    if headers is None:
        headers = {"Origin": str(client.base_url).rstrip("/")}
    return client.post(path, data=data, headers=headers, follow_redirects=False)


class _CSRFInputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokens: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "input" and attributes.get("type") == "hidden" and attributes.get("name") == "csrf_token":
            value = attributes.get("value")
            if value:
                self.tokens.add(value)


def post_with_csrf(client, response, path, **form):
    assert response.status_code == 200, f"CSRF page returned {response.status_code}"
    inputs = _CSRFInputs()
    inputs.feed(response.text)
    # Multiple forms on a page can carry the same browser CSRF token.
    assert len(inputs.tokens) == 1, "Expected one CSRF token value on the page"
    token, = inputs.tokens
    return post(client, path, csrf_token=token, **form)


def google(client, oidc, *, login_only=False):
    response = client.get("/api/v1/identity/register/google", params={"login": "1"} if login_only else None, follow_redirects=False)
    assert response.status_code in (302, 303), response.text
    state = parse_qs(urlparse(response.headers["location"]).query)["state"][0]
    params = {"state": state, "error": "access_denied"} if oidc.failure == "cancel" else {"state": state, "code": "valid"}
    return client.get(GOOGLE_CALLBACK, params=params, follow_redirects=False)


def login(client, identifier, password="123456", *, portal=False):
    path = "/api/v1/identity/portal/login" if portal else "/api/v1/identity/login"
    return post(client, path, identifier=identifier, password=password)


def signed_in(world, email, *, portal=False, client=None):
    client = client or world.new_client()
    response = login(client, email, portal=portal)
    assert response.status_code == 303, response.text
    return client


def submit(client, path, **form):
    return post_with_csrf(client, client.get(path, follow_redirects=False), path, **form)


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
