"""UC-21 theo dõi, UC-22 hủy, UC-23 xác nhận."""

from __future__ import annotations

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import service
from app.modules.ordering.exceptions import (
    CancelNotAllowedError,
    UnpaidQrConfirmError,
)
from tests.ordering.conftest import DemoIds, get_stock, prepare_cart, sample_shipping


@pytest.mark.asyncio
async def test_uc21_ac1_list_customer_orders(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    views, total = await service.list_customer_orders(db, demo.customer_key)
    assert total >= 1
    assert any(v.order_code == order.order_code for v in views)


@pytest.mark.asyncio
async def test_uc22_ac1_customer_cancel_restores_stock(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    inv, pricing = await prepare_cart(db, demo, qty=2, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    assert await get_stock(db, demo.variant_do_m) == 3
    await service.cancel_order_by_customer(
        db,
        account_key=demo.customer_key,
        order_code=order.order_code,
        inventory=inv,
    )
    assert await get_stock(db, demo.variant_do_m) == 5
    view = await service.get_customer_order(
        db, account_key=demo.customer_key, order_code=order.order_code
    )
    assert view.status == "CANCELLED"


@pytest.mark.asyncio
async def test_uc22_ac5_customer_cannot_cancel_confirmed(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    await service.confirm_order(
        db, employee_key=demo.employee_key, order_code=order.order_code
    )
    with pytest.raises(CancelNotAllowedError):
        await service.cancel_order_by_customer(
            db,
            account_key=demo.customer_key,
            order_code=order.order_code,
            inventory=inv,
        )


@pytest.mark.asyncio
async def test_uc23_ac1_confirm_cod(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    stock_before = await get_stock(db, demo.variant_do_m)
    confirmed = await service.confirm_order(
        db, employee_key=demo.employee_key, order_code=order.order_code
    )
    assert confirmed.order_status == "CONFIRMED"
    assert await get_stock(db, demo.variant_do_m) == stock_before


@pytest.mark.asyncio
async def test_uc23_ac3_reject_unpaid_qr_order(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_qr_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    with pytest.raises(UnpaidQrConfirmError):
        await service.confirm_order(
            db, employee_key=demo.employee_key, order_code=order.order_code
        )
