"""Hàm hỗ trợ xác thực đầu vào, thời gian UTC và tạo OTP."""

from datetime import UTC, datetime
from secrets import randbelow

from email_validator import EmailNotValidError, validate_email


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


def generate_otp() -> str:
    return f"{randbelow(1_000_000):06d}"
