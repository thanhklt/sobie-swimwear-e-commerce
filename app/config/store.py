"""Cấu hình thông tin cửa hàng hiển thị trên storefront."""

from app.config.settings import Config

STORE_HOTLINE = "0901234567"
STORE_ZALO_URL = "https://zalo.me/0901234567"

try:
    STORE_SHIPPING_FEE = int(getattr(Config, "SHIPPING_FEE", None) or 12_000)
except ValueError:
    STORE_SHIPPING_FEE = 12_000
