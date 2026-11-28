"""Đăng ký các router của module identity."""

from fastapi import APIRouter

from . import account, admin, auth, registration
from .account import storefront_identity_home

__all__ = ("router", "storefront_identity_home")

router = APIRouter(prefix="/api/v1/identity")
router.include_router(registration.router)
router.include_router(auth.router)
router.include_router(account.router)
router.include_router(admin.router)
