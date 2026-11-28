"""Kiểm tra Origin của yêu cầu ghi từ trình duyệt."""

import re
from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from app.config.settings import Config

_AUTHORITY = re.compile(r"(?:[a-zA-Z0-9._-]+|\[[a-fA-F0-9:.]+\])(?::[0-9]+)?")


def _parse_origin(value: str) -> tuple[str, str, int] | None:
    scheme, _, authority = value.partition("://")
    scheme = scheme.lower()
    if scheme not in ("http", "https") or not _AUTHORITY.fullmatch(authority):
        return None
    try:
        url = urlsplit(f"{scheme}://{authority}")
        hostname = url.hostname
        port = url.port
    except ValueError:
        return None
    if hostname is None:
        return None
    return scheme, hostname, port if port is not None else (443 if scheme == "https" else 80)


def has_allowed_origin(request: Request) -> bool:
    origins = request.headers.getlist("origin")
    if len(origins) != 1 or (origin := _parse_origin(origins[0])) is None:
        return False

    protos = request.headers.getlist("x-forwarded-proto")
    hosts = request.headers.getlist("x-forwarded-host")
    # The reverse proxy must overwrite client-supplied forwarding headers.
    if len(protos) <= 1 and len(hosts) <= 1:
        scheme = protos[0] if protos else request.url.scheme
        host = hosts[0] if hosts else request.headers.get("host", request.url.netloc)
        if origin == _parse_origin(f"{scheme}://{host}"):
            return True
    return any(origin == _parse_origin(value.strip()) for value in Config.ALLOWED_ORIGINS.split(","))


def origin_rejected() -> PlainTextResponse:
    return PlainTextResponse(
        "Nguồn yêu cầu không hợp lệ.",
        status_code=403,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
