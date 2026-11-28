"""Schema đầu vào / đầu ra của module shopping (DTO), tách biệt model lưu trữ."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GuestCartLine:
    """Một dòng giỏ khách vãng lai (localStorage) gửi lên khi gộp."""

    variant_key: UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class CartLineView:
    variant_key: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    is_available: bool
    unavailable_reason: str | None


@dataclass(frozen=True, slots=True)
class CartView:
    account_key: UUID
    lines: tuple[CartLineView, ...]
    subtotal: Decimal


@dataclass(frozen=True, slots=True)
class WishlistItemView:
    product_key: UUID
    product_id: str
    name: str
    image_url: str | None
    min_price: Decimal
    is_active: bool
    can_open_detail: bool


@dataclass(frozen=True, slots=True)
class WishlistView:
    account_key: UUID
    items: tuple[WishlistItemView, ...]
    page: int
    page_size: int
    total_items: int
