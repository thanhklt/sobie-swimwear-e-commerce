"""Adapter tạm [GD] đọc/ghi inventory + catalog cho ordering (UI + test)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text

from app.modules.ordering.exceptions import InsufficientStockError

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

DEMO_CUSTOMER_EMAIL = "khachhang@example.com"
DEMO_EMPLOYEE_EMAIL = "nhanvien@example.com"


async def get_account_key_by_email(db: AsyncSession, email: str) -> UUID:
    result = await db.exec(
        text("SELECT account_key FROM identity.account WHERE account_email = :email"),
        params={"email": email},
    )
    row = result.first()
    if row is None:
        raise RuntimeError(f"Không tìm thấy account {email}")
    return UUID(str(row[0]))


class DbInventoryGateway:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        result = await self._db.exec(
            text(
                """
                SELECT COALESCE(stock_quantity, 0)
                FROM inventory.stock WHERE stock_variant_key = :vk
                """
            ),
            params={"vk": variant_key},
        )
        row = result.first()
        return int(row[0]) if row else 0

    async def get_cost_price(self, variant_key: UUID) -> Decimal:
        result = await self._db.exec(
            text(
                """
                SELECT COALESCE(stock_cost_price, 0)
                FROM inventory.stock WHERE stock_variant_key = :vk
                """
            ),
            params={"vk": variant_key},
        )
        row = result.first()
        return Decimal(row[0] if row else 0)

    async def deduct_stock(self, variant_key: UUID, quantity: int) -> None:
        result = await self._db.exec(
            text(
                """
                UPDATE inventory.stock
                SET stock_quantity = stock_quantity - :qty
                WHERE stock_variant_key = :vk
                  AND stock_quantity >= :qty
                RETURNING stock_quantity
                """
            ),
            params={"vk": variant_key, "qty": quantity},
        )
        if result.first() is None:
            raise InsufficientStockError(str(variant_key))

    async def restore_stock(self, variant_key: UUID, quantity: int) -> None:
        await self._db.exec(
            text(
                """
                UPDATE inventory.stock
                SET stock_quantity = stock_quantity + :qty
                WHERE stock_variant_key = :vk
                """
            ),
            params={"vk": variant_key, "qty": quantity},
        )


class DbCatalogPricing:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_unit_price(self, variant_key: UUID) -> Decimal:
        result = await self._db.exec(
            text(
                "SELECT variant_sell_price FROM catalog.variant WHERE variant_key = :vk"
            ),
            params={"vk": variant_key},
        )
        return Decimal(result.one()[0])

    async def get_variant_label(self, variant_key: UUID) -> str:
        result = await self._db.exec(
            text(
                """
                SELECT p.product_name || ' — ' || c.color_name || ' / ' || s.size_name
                FROM catalog.variant v
                JOIN catalog.product p ON p.product_key = v.variant_product_key
                JOIN catalog.color c ON c.color_key = v.variant_color_key
                JOIN catalog.size s ON s.size_key = v.variant_size_key
                WHERE v.variant_key = :vk
                """
            ),
            params={"vk": variant_key},
        )
        row = result.first()
        return str(row[0]) if row else str(variant_key)
