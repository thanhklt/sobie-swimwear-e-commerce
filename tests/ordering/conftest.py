"""Fixture ordering — PostgreSQL docker."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import pytest_asyncio
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering.adapters import (
    DEMO_CUSTOMER_EMAIL,
    DEMO_EMPLOYEE_EMAIL,
    DbCatalogPricing,
    DbInventoryGateway,
    get_account_key_by_email,
)
from app.modules.ordering.schemas import ShippingInfo
from app.modules.shopping import service as shopping_service
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
    row = (
        await db.exec(
            text("SELECT variant_key FROM catalog.variant WHERE variant_id = :vid"),
            params={"vid": VARIANT_DO_M},
        )
    ).one()
    return DemoIds(
        customer_key=customer,
        employee_key=employee,
        variant_do_m=UUID(str(row[0])),
    )


@pytest_asyncio.fixture
async def clean_cart(db: AsyncSession, demo: DemoIds) -> None:
    await db.exec(
        text(
            """
            DELETE FROM shopping.cart_item
            WHERE cart_item_cart_key = (
              SELECT cart_key FROM shopping.cart WHERE cart_account_key = :ak
            )
            """
        ),
        params={"ak": demo.customer_key},
    )
    await db.commit()


async def set_stock(db: AsyncSession, variant_key: UUID, qty: int) -> None:
    await db.exec(
        text(
            """
            UPDATE inventory.stock SET stock_quantity = :qty
            WHERE stock_variant_key = :vk
            """
        ),
        params={"qty": qty, "vk": variant_key},
    )
    await db.commit()


async def get_stock(db: AsyncSession, variant_key: UUID) -> int:
    row = (
        await db.exec(
            text(
                "SELECT stock_quantity FROM inventory.stock WHERE stock_variant_key = :vk"
            ),
            params={"vk": variant_key},
        )
    ).one()
    return int(row[0])


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
