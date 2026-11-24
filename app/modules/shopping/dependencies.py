"""Protocol tạm để shopping gọi catalog / inventory qua interface công khai.

[GD] Teammate module catalog / inventory sẽ cung cấp service thật khớp các protocol này.
Shopping không truy vấn bảng của module khác.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID


class VariantAvailability(Protocol):
    """Tồn kho và trạng thái bán của biến thể (inventory + catalog)."""

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        """Số lượng tồn hiện tại; biến thể không tồn tại → báo lỗi phía caller."""
        ...

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        """True nếu sản phẩm đang bán (ACTIVE) và biến thể còn dùng được."""
        ...


class VariantPricing(Protocol):
    """Giá bán hiện tại của biến thể (catalog; có thể đã gồm KM sản phẩm)."""

    async def get_current_unit_price(self, variant_key: UUID) -> Decimal:
        """Đơn giá hiện tại (VND Decimal nguyên hoặc sẽ được làm tròn ROUND_HALF_UP)."""
        ...


class ProductCatalog(Protocol):
    """Thông tin sản phẩm cho wishlist (catalog)."""

    async def product_exists(self, product_key: UUID) -> bool:
        ...

    async def is_product_active(self, product_key: UUID) -> bool:
        """True nếu Đang bán; False nếu Ngừng bán."""
        ...

    async def get_product_card(self, product_key: UUID) -> ProductCardData:
        ...


class ProductCardData:
    """Dữ liệu hiển thị thẻ sản phẩm trên wishlist — do catalog cung cấp."""

    __slots__ = ("product_key", "product_id", "name", "image_url", "min_price", "is_active")

    def __init__(
        self,
        *,
        product_key: UUID,
        product_id: str,
        name: str,
        image_url: str | None,
        min_price: Decimal,
        is_active: bool,
    ) -> None:
        self.product_key = product_key
        self.product_id = product_id
        self.name = name
        self.image_url = image_url
        self.min_price = min_price
        self.is_active = is_active
