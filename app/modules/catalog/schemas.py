"""Validation cho form catalog."""
import re
from urllib.parse import urlsplit
from uuid import UUID

class CatalogError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message, self.status = message, status

def key(value):
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise CatalogError("Khóa không hợp lệ") from None

def name(value, limit=255, collapse=False):
    value = " ".join(value.split()) if collapse else value.strip()
    if not value or len(value) > limit:
        raise CatalogError(f"Tên bắt buộc, tối đa {limit} ký tự")
    return value

def status(value):
    if value not in {"ACTIVE", "INACTIVE"}:
        raise CatalogError("Trạng thái không hợp lệ")
    return value

def price(value):
    if not re.fullmatch(r"[0-9]{1,12}", value) or int(value) == 0:
        raise CatalogError("Giá phải là số nguyên VND từ 1 đến 999999999999")
    return int(value)

def image_url(value):
    value = value.strip()
    try:
        parts = urlsplit(value)
    except ValueError:
        raise CatalogError("URL ảnh không hợp lệ") from None
    if len(value) > 500 or not (
        (parts.scheme in {"http", "https"} and parts.netloc and not parts.username)
        or (value.startswith("/static/") and not parts.scheme and not parts.netloc)
    ):
        raise CatalogError("Ảnh phải là URL http/https hoặc đường dẫn /static/")
    return value
