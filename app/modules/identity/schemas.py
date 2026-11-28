"""Kiểu dữ liệu và lỗi dùng chung của module identity."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class SessionPortal(StrEnum):
    STOREFRONT = "storefront"
    PORTAL = "portal"


@dataclass(frozen=True, slots=True)
class AuthenticatedSession:
    session_key: UUID
    account_key: UUID
    role: Role


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"


@dataclass(frozen=True, slots=True)
class Account:
    account_key: UUID
    email: str
    google_sub: str | None
    role: Role
    status: str
    password_hash: str | None = None


@dataclass(frozen=True, slots=True)
class RegistrationResult:
    stage: str = "email"
    message: str = ""
    email: str = ""
    field: str = ""
    status: int = 200
    location: str = ""
    session_token: str = ""
    otp_locked: bool = False
    checkout: bool = False
    resend_after: int = 0


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
