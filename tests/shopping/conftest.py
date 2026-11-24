"""Fixture DB cho tests/shopping — dùng PostgreSQL docker (infra/docker-compose).

Lưu ý: không để nhiều async fixture cùng đọc một AsyncSession song song
(asyncpg: another operation is in progress).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping.dependencies import ProductCardData
from app.shared.database.engine import session_factory
from tests.shopping.fakes import FakeAvailability, FakePricing, FakeProductCatalog

DEMO_EMAIL = "khachhang@example.com"
VARIANT_DO_M = "SP-0002-DO-M"
VARIANT_XANH_S = "SP-0002-XANHDUONG-S"
PRODUCT_SP1 = "SP-0001"
PRODUCT_SP2 = "SP-0002"


@dataclass(frozen=True, slots=True)
class DemoIds:
    account_key: UUID
    variant_do_m: UUID
    variant_xanh_s: UUID
    product_sp1: UUID
    product_sp2: UUID


@pytest_asyncio.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
        if session.in_transaction():
            await session.rollback()


@pytest_asyncio.fixture
async def demo(db: AsyncSession) -> DemoIds:
    """Load mọi UUID seed trong một lượt — tránh fixture song song trên cùng session."""
    account = (
        await db.exec(
            text(
                "SELECT account_key FROM identity.account WHERE account_email = :email"
            ),
            params={"email": DEMO_EMAIL},
        )
    ).one()[0]
    do_m = (
        await db.exec(
            text("SELECT variant_key FROM catalog.variant WHERE variant_id = :vid"),
            params={"vid": VARIANT_DO_M},
        )
    ).one()[0]
    xanh = (
        await db.exec(
            text("SELECT variant_key FROM catalog.variant WHERE variant_id = :vid"),
            params={"vid": VARIANT_XANH_S},
        )
    ).one()[0]
    sp1 = (
        await db.exec(
            text("SELECT product_key FROM catalog.product WHERE product_id = :pid"),
            params={"pid": PRODUCT_SP1},
        )
    ).one()[0]
    sp2 = (
        await db.exec(
            text("SELECT product_key FROM catalog.product WHERE product_id = :pid"),
            params={"pid": PRODUCT_SP2},
        )
    ).one()[0]
    return DemoIds(
        account_key=UUID(str(account)),
        variant_do_m=UUID(str(do_m)),
        variant_xanh_s=UUID(str(xanh)),
        product_sp1=UUID(str(sp1)),
        product_sp2=UUID(str(sp2)),
    )


@pytest_asyncio.fixture
async def clean_cart(db: AsyncSession, demo: DemoIds) -> None:
    await db.exec(
        text(
            """
            DELETE FROM shopping.cart_merge_request
            WHERE cart_merge_request_account_key = :account_key
            """
        ),
        params={"account_key": demo.account_key},
    )
    await db.exec(
        text(
            """
            DELETE FROM shopping.cart_item
            WHERE cart_item_cart_key = (
              SELECT cart_key FROM shopping.cart WHERE cart_account_key = :account_key
            )
            """
        ),
        params={"account_key": demo.account_key},
    )
    await db.commit()


@pytest_asyncio.fixture
async def clean_wishlist(db: AsyncSession, demo: DemoIds) -> None:
    await db.exec(
        text(
            """
            DELETE FROM shopping.wishlist_item
            WHERE wishlist_item_wishlist_key = (
              SELECT wishlist_key FROM shopping.wishlist
              WHERE wishlist_account_key = :account_key
            )
            """
        ),
        params={"account_key": demo.account_key},
    )
    await db.commit()


async def db_cart_qty(
    db: AsyncSession, account_key: UUID, variant_key: UUID
) -> int | None:
    result = await db.exec(
        text(
            """
            SELECT ci.cart_item_quantity
            FROM shopping.cart_item ci
            JOIN shopping.cart c ON c.cart_key = ci.cart_item_cart_key
            WHERE c.cart_account_key = :account_key
              AND ci.cart_item_variant_key = :variant_key
            """
        ),
        params={"account_key": account_key, "variant_key": variant_key},
    )
    row = result.first()
    return int(row[0]) if row else None


async def db_stock(db: AsyncSession, variant_key: UUID) -> int:
    result = await db.exec(
        text(
            """
            SELECT stock_quantity FROM inventory.stock
            WHERE stock_variant_key = :variant_key
            """
        ),
        params={"variant_key": variant_key},
    )
    return int(result.one()[0])


async def set_stock(db: AsyncSession, variant_key: UUID, quantity: int) -> None:
    await db.exec(
        text(
            """
            UPDATE inventory.stock
            SET stock_quantity = :quantity
            WHERE stock_variant_key = :variant_key
            """
        ),
        params={"variant_key": variant_key, "quantity": quantity},
    )
    await db.commit()


def price_do_m() -> Decimal:
    return Decimal("300000")


def availability_for(
    variant_key: UUID, stock: int, *, sellable: bool = True
) -> FakeAvailability:
    return FakeAvailability({variant_key: stock}, {variant_key: sellable})


def pricing_for(variant_key: UUID, price: Decimal | int) -> FakePricing:
    return FakePricing({variant_key: price})


def catalog_for(*cards: ProductCardData) -> FakeProductCatalog:
    return FakeProductCatalog({c.product_key: c for c in cards})
