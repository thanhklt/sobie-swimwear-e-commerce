"""Fixture DB cho tests/shopping — dùng PostgreSQL docker (infra/docker-compose).

Hỗ trợ tests UC-18 (giỏ / gộp) và UC-38 (wishlist).

Lưu ý: không để nhiều async fixture cùng đọc một AsyncSession song song
(asyncpg: another operation is in progress).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import pytest_asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping import repository as shopping_repository
from app.modules.shopping.adapters import (
    DEMO_EMAIL,
    get_account_key_by_email,
    get_product_key_by_id,
    get_stock_quantity,
    get_variant_key_by_id,
    set_stock_quantity,
)
from app.modules.shopping.dependencies import ProductCardData
from app.modules.shopping.models import CartItem, CartMergeRequest, WishlistItem
from app.shared.database.engine import session_factory
from tests.shopping.fakes import FakeAvailability, FakePricing, FakeProductCatalog

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
    return DemoIds(
        account_key=await get_account_key_by_email(db, DEMO_EMAIL),
        variant_do_m=await get_variant_key_by_id(db, VARIANT_DO_M),
        variant_xanh_s=await get_variant_key_by_id(db, VARIANT_XANH_S),
        product_sp1=await get_product_key_by_id(db, PRODUCT_SP1),
        product_sp2=await get_product_key_by_id(db, PRODUCT_SP2),
    )


@pytest_asyncio.fixture
async def clean_cart(db: AsyncSession, demo: DemoIds) -> None:
    merge_rows = await db.exec(
        select(CartMergeRequest).where(
            CartMergeRequest.cart_merge_request_account_key == demo.account_key
        )
    )
    for row in merge_rows.all():
        await db.delete(row)

    cart_key = await shopping_repository.get_cart_key(db, demo.account_key)
    if cart_key is not None:
        items = await db.exec(
            select(CartItem).where(CartItem.cart_item_cart_key == cart_key)
        )
        for item in items.all():
            await db.delete(item)
    await db.commit()


@pytest_asyncio.fixture
async def clean_wishlist(db: AsyncSession, demo: DemoIds) -> None:
    wishlist_key = await shopping_repository.get_wishlist_key(db, demo.account_key)
    if wishlist_key is not None:
        items = await db.exec(
            select(WishlistItem).where(
                WishlistItem.wishlist_item_wishlist_key == wishlist_key
            )
        )
        for item in items.all():
            await db.delete(item)
    await db.commit()


async def db_cart_qty(
    db: AsyncSession, account_key: UUID, variant_key: UUID
) -> int | None:
    cart_key = await shopping_repository.get_cart_key(db, account_key)
    if cart_key is None:
        return None
    row = await shopping_repository.get_cart_item_quantity(db, cart_key, variant_key)
    if row is None:
        return None
    return row[1]


async def db_stock(db: AsyncSession, variant_key: UUID) -> int:
    return await get_stock_quantity(db, variant_key)


async def set_stock(db: AsyncSession, variant_key: UUID, quantity: int) -> None:
    await set_stock_quantity(db, variant_key, quantity)
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
