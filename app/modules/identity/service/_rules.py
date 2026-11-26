"""Xác thực đầu vào, quy tắc hồ sơ và thời gian của identity."""

import re
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from unicodedata import normalize

from email_validator import EmailNotValidError, validate_email

from ..schemas import AccountFormError, PROFILE_FIELDS, Role, SessionPortal


SESSION_POLICIES = {
    SessionPortal.STOREFRONT: ((Role.CUSTOMER,), timedelta(minutes=30)),
    SessionPortal.PORTAL: ((Role.EMPLOYEE, Role.ADMIN), timedelta(hours=1)),
}
VIETNAM_TIMEZONE = "Asia/Ho_Chi_Minh"


def normalize_email(value: str) -> str:
    if len(value) > 255:
        raise ValueError("Email không hợp lệ")
    try:
        return validate_email(
            value.strip(), check_deliverability=False, allow_smtputf8=False
        ).normalized.lower()
    except EmailNotValidError as exc:
        raise ValueError("Email không hợp lệ") from exc


def password_validation_error(password: str, confirmation: str) -> str | None:
    if not password or not confirmation:
        return "Vui lòng nhập mật khẩu và xác nhận mật khẩu."
    if len(password) < 6:
        return "Mật khẩu phải có ít nhất 6 ký tự."
    if len(password.encode("utf-8")) > 72 or "\x00" in password:
        return "Mật khẩu phải có tối đa 72 byte và không chứa ký tự rỗng."
    if password != confirmation:
        return "Mật khẩu xác nhận không khớp."
    return None


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_timestamp() -> float:
    return utc_now().timestamp()


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def profile_values(account) -> dict[str, str]:
    return {field: str(getattr(account, f"account_{field}") or "") for field in PROFILE_FIELDS}


def validate_profile(
    fields: dict[str, str], role: Role, *, creating: bool = False, include_email: bool = True
) -> dict:
    values = {}
    for field, (label, limit) in PROFILE_FIELDS.items():
        if field == "email" and not include_email:
            continue
        value = fields.get(field, "").strip()
        if len(value) > limit or "\x00" in value:
            raise AccountFormError(field, f"{label} không hợp lệ")
        if field == "name" and not value:
            raise AccountFormError(field, "Vui lòng nhập họ tên")
        if field == "email":
            try:
                value = normalize_email(value)
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
                if value > utc_now().date():
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
