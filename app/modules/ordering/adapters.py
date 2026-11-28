"""Adapter tạm [GD] đọc/ghi inventory + catalog + identity cho ordering (UI + test).

Dùng SQLModel ORM map bảng module khác (chỉ cột cần thiết). Thay bằng service
công khai của catalog / inventory / identity khi teammate sẵn sàng.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import col, select

from app.modules.ordering.exceptions import InsufficientStockError
from app.shared.seed_refs import (
    AccountRef,
    ColorRef,
    ProductRef,
    SizeRef,
    StockRef,
    VariantRef,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

DEMO_CUSTOMER_EMAIL = "khachhang@example.com"
DEMO_EMPLOYEE_EMAIL = "nhanvien@example.com"


async def get_account_key_by_email(db: AsyncSession, email: str) -> UUID:
    result = await db.exec(
        select(AccountRef).where(AccountRef.account_email == email)
    )
    account = result.first()
    if account is None:
        raise RuntimeError(f"Không tìm thấy account {email}")
    return account.account_key


async def get_variant_key_by_id(db: AsyncSession, variant_id: str) -> UUID:
    result = await db.exec(
        select(VariantRef).where(VariantRef.variant_id == variant_id)
    )
    variant = result.first()
    if variant is None:
        raise RuntimeError(f"Không tìm thấy variant {variant_id}")
    return variant.variant_key


class DbInventoryGateway:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def _get_stock(self, variant_key: UUID) -> StockRef | None:
        result = await self._db.exec(
            select(StockRef).where(StockRef.stock_variant_key == variant_key)
        )
        return result.first()

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        stock = await self._get_stock(variant_key)
        return int(stock.stock_quantity) if stock else 0

    async def get_cost_price(self, variant_key: UUID) -> Decimal:
        stock = await self._get_stock(variant_key)
        return Decimal(stock.stock_cost_price if stock else 0)

    async def set_stock_quantity(self, variant_key: UUID, quantity: int) -> None:
        """Helper test/UI seed — gán tồn tuyệt đối."""
        result = await self._db.exec(
            select(StockRef)
            .where(StockRef.stock_variant_key == variant_key)
            .with_for_update()
        )
        stock = result.first()
        if stock is None:
            raise RuntimeError(f"Không có dòng stock cho {variant_key}")
        stock.stock_quantity = quantity
        self._db.add(stock)
        await self._db.flush()

    async def deduct_stock(self, variant_key: UUID, quantity: int) -> None:
        result = await self._db.exec(
            select(StockRef)
            .where(StockRef.stock_variant_key == variant_key)
            .with_for_update()
        )
        stock = result.first()
        if stock is None or stock.stock_quantity < quantity:
            raise InsufficientStockError(str(variant_key))
        stock.stock_quantity -= quantity
        self._db.add(stock)
        await self._db.flush()

    async def restore_stock(self, variant_key: UUID, quantity: int) -> None:
        result = await self._db.exec(
            select(StockRef)
            .where(StockRef.stock_variant_key == variant_key)
            .with_for_update()
        )
        stock = result.first()
        if stock is None:
            raise RuntimeError(f"Không có dòng stock cho {variant_key}")
        stock.stock_quantity += quantity
        self._db.add(stock)
        await self._db.flush()


class DbCatalogPricing:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_unit_price(self, variant_key: UUID) -> Decimal:
        result = await self._db.exec(
            select(VariantRef).where(VariantRef.variant_key == variant_key)
        )
        variant = result.one()
        return Decimal(variant.variant_sell_price or 0)

    async def get_variant_label(self, variant_key: UUID) -> str:
        result = await self._db.exec(
            select(ProductRef.product_name, ColorRef.color_name, SizeRef.size_name)
            .select_from(VariantRef)
            .join(ProductRef, col(ProductRef.product_key) == col(VariantRef.variant_product_key))
            .join(ColorRef, col(ColorRef.color_key) == col(VariantRef.variant_color_key))
            .join(SizeRef, col(SizeRef.size_key) == col(VariantRef.variant_size_key))
            .where(VariantRef.variant_key == variant_key)
        )
        row = result.first()
        if row is None:
            return str(variant_key)
        product_name, color_name, size_name = row
        return f"{product_name} — {color_name} / {size_name}"
