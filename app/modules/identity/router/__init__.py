"""Đăng ký các router của module identity."""

from fastapi import APIRouter

from . import account, admin, auth, registration
from .account import storefront_identity_home

__all__ = ("router", "origin_protected_paths", "storefront_identity_home")

router = APIRouter(prefix="/api/v1/identity")
router.include_router(registration.router)
router.include_router(auth.router)
router.include_router(account.router)
router.include_router(admin.router)

_ORIGIN_PROTECTED_ROUTE_NAMES = (
    "request_registration_otp",
    "resend_registration_otp",
    "verify_registration_otp",
    "create_registration_password",
    "storefront_password_login",
    "portal_password_login",
    "storefront_logout",
    "portal_logout",
)
# Resolve paths after including the child routers, including the parent's prefix.
origin_protected_paths = frozenset(str(router.url_path_for(name)) for name in _ORIGIN_PROTECTED_ROUTE_NAMES)
