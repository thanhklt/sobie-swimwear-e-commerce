"""UC-18 — các AC giỏ hàng cốt lõi (service + DB)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping import service
from app.modules.shopping.exceptions import InsufficientStockError, InvalidQuantityError
from app.shared.database.engine import session_factory
from tests.shopping.conftest import (
    DemoIds,
    availability_for,
    db_cart_qty,
    db_stock,
    price_do_m,
    pricing_for,
    set_stock,
)


@pytest.mark.asyncio
async def test_uc18_ac1_add_item_to_cart(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-1: thêm biến thể còn hàng → 1 dòng đúng SL; không trừ tồn."""
    await set_stock(db, demo.variant_do_m, 5)
    stock_before = await db_stock(db, demo.variant_do_m)

    qty = await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=2,
        availability=availability_for(demo.variant_do_m, 5),
    )
    assert qty == 2
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 2

    cart = await service.get_cart(
        db,
        account_key=demo.account_key,
        availability=availability_for(demo.variant_do_m, 5),
        pricing=pricing_for(demo.variant_do_m, price_do_m()),
    )
    assert len(cart.lines) == 1
    assert cart.lines[0].quantity == 2
    assert cart.subtotal == Decimal("600000")
    assert await db_stock(db, demo.variant_do_m) == stock_before


@pytest.mark.asyncio
async def test_uc18_ac2_add_existing_variant(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-2: thêm biến thể đã có → cộng dồn số lượng trên 1 dòng."""
    await set_stock(db, demo.variant_do_m, 5)
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=2,
        availability=availability_for(demo.variant_do_m, 5),
    )
    qty = await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=1,
        availability=availability_for(demo.variant_do_m, 5),
    )
    assert qty == 3
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 3


@pytest.mark.asyncio
async def test_uc18_ac3_reject_quantity_over_stock(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-3: sửa SL vượt tồn → từ chối, giữ SL cũ."""
    await set_stock(db, demo.variant_do_m, 3)
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=2,
        availability=availability_for(demo.variant_do_m, 3),
    )
    with pytest.raises(InsufficientStockError) as exc:
        await service.set_cart_item_quantity(
            db,
            account_key=demo.account_key,
            variant_key=demo.variant_do_m,
            quantity=4,
            availability=availability_for(demo.variant_do_m, 3),
        )
    assert exc.value.message == "Chỉ còn 3 sản phẩm"
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 2


@pytest.mark.asyncio
async def test_uc18_ac4_remove_cart_line(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-4: xóa 1 dòng → giỏ còn dòng kia, tạm tính cập nhật."""
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=1,
        availability=availability_for(demo.variant_do_m, 10),
    )
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_xanh_s,
        quantity=1,
        availability=availability_for(demo.variant_xanh_s, 10),
    )
    await service.remove_cart_item(
        db, account_key=demo.account_key, variant_key=demo.variant_xanh_s
    )
    assert await db_cart_qty(db, demo.account_key, demo.variant_xanh_s) is None
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 1

    cart = await service.get_cart(
        db,
        account_key=demo.account_key,
        availability=_MultiAvail(
            {demo.variant_do_m: 10, demo.variant_xanh_s: 10}
        ),
        pricing=_MultiPrice(
            {demo.variant_do_m: price_do_m(), demo.variant_xanh_s: Decimal("290000")}
        ),
    )
    assert len(cart.lines) == 1
    assert cart.subtotal == price_do_m()


@pytest.mark.asyncio
async def test_uc18_ac7_out_of_stock_line_excluded_from_subtotal(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-7 / E2: hết hàng → giữ dòng, gắn nhãn, không tính tạm tính."""
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_xanh_s,
        quantity=1,
        availability=availability_for(demo.variant_xanh_s, 5),
    )
    cart = await service.get_cart(
        db,
        account_key=demo.account_key,
        availability=availability_for(demo.variant_xanh_s, 0),
        pricing=pricing_for(demo.variant_xanh_s, Decimal("290000")),
    )
    assert len(cart.lines) == 1
    assert cart.lines[0].is_available is False
    assert cart.lines[0].unavailable_reason == "Hết hàng"
    assert cart.subtotal == Decimal("0")
    assert await db_cart_qty(db, demo.account_key, demo.variant_xanh_s) == 1


@pytest.mark.asyncio
async def test_uc18_ac8_cart_persisted_on_account(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 AC-8: giỏ KH lưu theo tài khoản (đọc lại bằng session khác)."""
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=1,
        availability=availability_for(demo.variant_do_m, 10),
    )
    async with session_factory() as db_b:
        cart = await service.get_cart(
            db_b,
            account_key=demo.account_key,
            availability=availability_for(demo.variant_do_m, 10),
            pricing=pricing_for(demo.variant_do_m, price_do_m()),
        )
    assert len(cart.lines) == 1
    assert cart.lines[0].quantity == 1


@pytest.mark.asyncio
async def test_uc18_e3_invalid_quantity(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-18 E3: số lượng không hợp lệ (≤ 0) → từ chối."""
    with pytest.raises(InvalidQuantityError):
        await service.add_item_to_cart(
            db,
            account_key=demo.account_key,
            variant_key=demo.variant_do_m,
            quantity=0,
            availability=availability_for(demo.variant_do_m, 5),
        )


class _MultiAvail:
    def __init__(self, stock: dict[UUID, int]):
        self.stock = stock

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        return self.stock[variant_key]

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        return True


class _MultiPrice:
    def __init__(self, prices: dict[UUID, Decimal]):
        self.prices = prices

    async def get_current_unit_price(self, variant_key: UUID) -> Decimal:
        return self.prices[variant_key]
