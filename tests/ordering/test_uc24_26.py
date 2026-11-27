"""UC-24 tự hủy QR quá hạn; UC-26 hóa đơn."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import repository, service
from tests.ordering.conftest import DemoIds, get_stock, prepare_cart, sample_shipping


@pytest.mark.asyncio
async def test_uc24_ac1_cancel_overdue_qr(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-24 AC-1: QR UNPAID quá 24h → tự hủy, hoàn tồn."""
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_qr_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    order_key = order.order_key
    order_code = order.order_code
    # Lùi created_date > 24h
    loaded = await repository.get_order_by_key(db, order_key)
    assert loaded is not None
    loaded.order_created_date = datetime.now(UTC) - timedelta(hours=25)
    await repository.save_order(db, loaded)
    await db.commit()

    cancelled = await service.auto_cancel_overdue_qr_orders(
        db, inventory=inv, now=datetime.now(UTC)
    )
    assert order_code in cancelled
    assert await get_stock(db, demo.variant_do_m) == 5


@pytest.mark.asyncio
async def test_uc24_ac2_not_yet_overdue(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-24 AC-2: QR còn trong hạn → không tự hủy."""
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_qr_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    cancelled = await service.auto_cancel_overdue_qr_orders(
        db, inventory=inv, now=datetime.now(UTC)
    )
    assert order.order_code not in cancelled


@pytest.mark.asyncio
async def test_uc26_ac1_issue_invoice_on_delivered(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-26 AC-1: giao thành công → xuất HD-{code}, payment PAID."""
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
    await service.transition_status_for_shipping(
        db, order_code=order.order_code, to_status="AWAITING_PICKUP", source="EMPLOYEE"
    )
    await service.transition_status_for_shipping(
        db, order_code=order.order_code, to_status="SHIPPING"
    )
    await service.transition_status_for_shipping(
        db, order_code=order.order_code, to_status="DELIVERED"
    )
    inv_view = await service.get_invoice_for_customer(
        db, account_key=demo.customer_key, order_code=order.order_code
    )
    assert inv_view.invoice_id == f"HD-{order.order_code}"
    view = await service.get_customer_order(
        db, account_key=demo.customer_key, order_code=order.order_code
    )
    assert view.payment_status == "PAID"


@pytest.mark.asyncio
async def test_uc26_ac3_invoice_idempotent(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-26 AC-3: xuất hóa đơn lặp lại → cùng invoice_id."""
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    order_code = order.order_code
    await service.confirm_order(
        db, employee_key=demo.employee_key, order_code=order_code
    )
    await service.transition_status_for_shipping(
        db, order_code=order_code, to_status="AWAITING_PICKUP", source="EMPLOYEE"
    )
    await service.transition_status_for_shipping(
        db, order_code=order_code, to_status="SHIPPING"
    )
    await service.transition_status_for_shipping(
        db, order_code=order_code, to_status="DELIVERED"
    )
    a = await service.issue_invoice_for_delivered(db, order_code)
    b = await service.issue_invoice_for_delivered(db, order_code)
    assert a.invoice_id == b.invoice_id
