"""Kiểu dữ liệu phiên đăng nhập công khai của module identity."""

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
