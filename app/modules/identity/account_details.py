"""Trường hồ sơ dùng chung cho storefront và portal."""
from datetime import date
import re
from unicodedata import normalize

from app.modules.identity import helper
from app.modules.identity.session import Role


PROFILE_FIELDS = {
    "name": ("Họ tên", 255),
    "date_of_birth": ("Ngày sinh", 10),
    "house_number": ("Số nhà", 255),
    "ward": ("Phường/xã", 100),
    "city": ("Tỉnh/thành phố", 255),
    "country": ("Quốc gia", 100),
    "email": ("Email", 255),
    "phone_number": ("Số điện thoại", 20),
}


class AccountFormError(Exception):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field


def profile_values(account) -> dict[str, str]:
    return {field: str(getattr(account, f"account_{field}") or "") for field in PROFILE_FIELDS}


def validate_profile(fields: dict[str, str], role: Role, *, creating: bool = False) -> dict:
    values = {}
    for field, (label, limit) in PROFILE_FIELDS.items():
        value = fields.get(field, "").strip()
        if len(value) > limit or "\x00" in value:
            raise AccountFormError(field, f"{label} không hợp lệ")
        if field == "name" and not value:
            raise AccountFormError(field, "Vui lòng nhập họ tên")
        if field == "email":
            try:
                value = helper.normalize_email(value)
            except ValueError as exc:
                raise AccountFormError(field, str(exc)) from exc
        if field == "phone_number" and (value or creating or role != Role.CUSTOMER):
            if not re.fullmatch(r"\+?[0-9]{8,15}", value):
                raise AccountFormError(field, "Số điện thoại không hợp lệ")
        if field == "date_of_birth":
            if value:
                try:
                    value = date.fromisoformat(value)
                except ValueError as exc:
                    raise AccountFormError(field, "Ngày sinh không hợp lệ") from exc
                if value > helper.utc_now().date():
                    raise AccountFormError(field, "Ngày sinh không hợp lệ")
            elif role != Role.CUSTOMER:
                raise AccountFormError(field, "Vui lòng nhập ngày sinh")
        values[f"account_{field}"] = value or None
    return values


def account_code_prefix(role: Role) -> str:
    return {Role.CUSTOMER: "KH", Role.EMPLOYEE: "NV", Role.ADMIN: "AD"}[role]


def internal_code_name(name: str) -> str:
    decomposed = normalize("NFD", name.upper().replace("Đ", "D"))
    return re.sub(r"[^A-Z0-9]", "", decomposed)
