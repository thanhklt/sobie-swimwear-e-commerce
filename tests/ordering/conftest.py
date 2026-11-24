"""Fixture ordering — PostgreSQL docker."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

import pytest_asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering.adapters import (
    DEMO_CUSTOMER_EMAIL,
    DEMO_EMPLOYEE_EMAIL,
    DbCatalogPricing,
    DbInventoryGateway,
    get_account_key_by_email,
    get_variant_key_by_id,
)
from app.modules.ordering.schemas import ShippingInfo
from app.modules.shopping import repository as shopping_repository
from app.modules.shopping import service as shopping_service
from app.modules.shopping.models import CartItem
from app.shared.database.engine import session_factory

VARIANT_DO_M = "SP-0002-DO-M"


@dataclass(frozen=True, slots=True)
class DemoIds:
    customer_key: UUID
    employee_key: UUID
    variant_do_m: UUID


@pytest_asyncio.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
        if session.in_transaction():
            await session.rollback()


@pytest_asyncio.fixture
async def demo(db: AsyncSession) -> DemoIds:
    customer = await get_account_key_by_email(db, DEMO_CUSTOMER_EMAIL)
    employee = await get_account_key_by_email(db, DEMO_EMPLOYEE_EMAIL)
    variant_do_m = await get_variant_key_by_id(db, VARIANT_DO_M)
    return DemoIds(
        customer_key=customer,
        employee_key=employee,
        variant_do_m=variant_do_m,
    )


@pytest_asyncio.fixture
async def clean_cart(db: AsyncSession, demo: DemoIds) -> None:
    cart_key = await shopping_repository.get_cart_key(db, demo.customer_key)
    if cart_key is not None:
        result = await db.exec(
            select(CartItem).where(CartItem.cart_item_cart_key == cart_key)
        )
        for item in result.all():
            await db.delete(item)
        await db.commit()


async def set_stock(db: AsyncSession, variant_key: UUID, qty: int) -> None:
    await DbInventoryGateway(db).set_stock_quantity(variant_key, qty)
    await db.commit()


async def get_stock(db: AsyncSession, variant_key: UUID) -> int:
    return await DbInventoryGateway(db).get_stock_quantity(variant_key)


def sample_shipping() -> ShippingInfo:
    return ShippingInfo(
        name="Khách Hàng Demo",
        phone="0900000003",
        house_number="273 An Dương Vương",
        ward="Phường Chợ Quán",
        city="TP. Hồ Chí Minh",
        country="Việt Nam",
    )


class StockAsAvailability:
    def __init__(self, stock: dict[UUID, int]):
        self.stock = stock

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        return self.stock[variant_key]

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        return True


async def prepare_cart(
    db: AsyncSession, demo: DemoIds, *, qty: int, stock: int
) -> tuple[DbInventoryGateway, DbCatalogPricing]:
    await set_stock(db, demo.variant_do_m, stock)
    await shopping_service.add_item_to_cart(
        db,
        account_key=demo.customer_key,
        variant_key=demo.variant_do_m,
        quantity=qty,
        availability=StockAsAvailability({demo.variant_do_m: stock}),
    )
    return DbInventoryGateway(db), DbCatalogPricing(db)
