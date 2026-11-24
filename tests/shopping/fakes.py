"""Fake protocol tạm cho catalog / inventory — chỉ dùng trong test shopping."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.modules.shopping.dependencies import ProductCardData


class FakeAvailability:
    def __init__(self, stock: dict[UUID, int], sellable: dict[UUID, bool] | None = None):
        self.stock = dict(stock)
        self.sellable = sellable if sellable is not None else {k: True for k in stock}

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        return int(self.stock.get(variant_key, 0))

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        return bool(self.sellable.get(variant_key, False))


class FakePricing:
    def __init__(self, prices: dict[UUID, Decimal | int]):
        self.prices = {k: Decimal(v) for k, v in prices.items()}

    async def get_current_unit_price(self, variant_key: UUID) -> Decimal:
        return self.prices[variant_key]


class FakeProductCatalog:
    def __init__(self, products: dict[UUID, ProductCardData]):
        self.products = products

    async def product_exists(self, product_key: UUID) -> bool:
        return product_key in self.products

    async def is_product_active(self, product_key: UUID) -> bool:
        return self.products[product_key].is_active

    async def get_product_card(self, product_key: UUID) -> ProductCardData:
        return self.products[product_key]
