"""UC-20 — đặt hàng QR."""

from __future__ import annotations

from datetime import UTC, timedelta

import pytest
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import service
from tests.ordering.conftest import DemoIds, get_stock, prepare_cart, sample_shipping


@pytest.mark.asyncio
async def test_uc20_ac1_create_qr_order(
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
    assert order.order_status == "PENDING"
    assert order.order_payment_status == "UNPAID"
    assert await get_stock(db, demo.variant_do_m) == 4

    view = await service.to_order_view(db, order)
    assert view.payment_name == "QR"
    assert view.payment_deadline is not None
    assert view.created_at + timedelta(hours=24) == view.payment_deadline
    assert view.show_qr is True
    assert view.transfer_content == f"SOBIE{order.order_code}"


@pytest.mark.asyncio
async def test_uc20_ac3_order_code_format(
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
    assert len(order.order_code) == 8
    assert all(c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for c in order.order_code)


@pytest.mark.asyncio
async def test_uc20_ac5_hide_qr_when_paid(
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
    await service.mark_order_paid_by_code(db, order.order_code)
    refreshed = await service.get_customer_order(
        db, account_key=demo.customer_key, order_code=order.order_code
    )
    assert refreshed.payment_status == "PAID"
    assert refreshed.show_qr is False
