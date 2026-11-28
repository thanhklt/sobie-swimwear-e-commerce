"""Protocol tạm [GD] — inventory / catalog / promotion cho ordering."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID


class InventoryGateway(Protocol):
    async def get_stock_quantity(self, variant_key: UUID) -> int: ...

    async def get_cost_price(self, variant_key: UUID) -> Decimal: ...

    async def deduct_stock(self, variant_key: UUID, quantity: int) -> None:
        """Trừ tồn atomic; không đủ thì raise InsufficientStockError (ordering)."""
        ...

    async def restore_stock(self, variant_key: UUID, quantity: int) -> None: ...


class CatalogPricing(Protocol):
    async def get_unit_price(self, variant_key: UUID) -> Decimal: ...

    async def get_variant_label(self, variant_key: UUID) -> str:
        """Tên hiển thị để snapshot / hóa đơn."""
        ...


class AppliedPromotion:
    __slots__ = (
        "discount_amount",
        "order_promotion_key",
        "code_promotion_key",
    )

    def __init__(
        self,
        *,
        discount_amount: Decimal,
        order_promotion_key: UUID | None = None,
        code_promotion_key: UUID | None = None,
    ) -> None:
        self.discount_amount = discount_amount
        self.order_promotion_key = order_promotion_key
        self.code_promotion_key = code_promotion_key


class PromotionGateway(Protocol):
    """UC-31 tạm: chọn tối đa 1 KM hóa đơn/voucher và consume/restore lượt."""

    async def quote(
        self,
        *,
        subtotal: Decimal,
        voucher_code: str | None,
    ) -> AppliedPromotion: ...

    async def consume(self, applied: AppliedPromotion) -> None: ...

    async def restore(self, applied: AppliedPromotion) -> None: ...


class NoPromotionGateway:
    """Không áp KM — dùng cho AC không liên quan promotion."""

    async def quote(
        self, *, subtotal: Decimal, voucher_code: str | None
    ) -> AppliedPromotion:
        return AppliedPromotion(discount_amount=Decimal("0"))

    async def consume(self, applied: AppliedPromotion) -> None:
        return None

    async def restore(self, applied: AppliedPromotion) -> None:
        return None
