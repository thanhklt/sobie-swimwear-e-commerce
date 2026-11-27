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
    """UC-21 AC-1: khách xem danh sách đơn của mình."""
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
    """UC-22 AC-1: khách hủy đơn PENDING → CANCELLED, hoàn tồn."""
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
    """UC-22 AC-5: khách không hủy được đơn đã CONFIRMED."""
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
    """UC-23 AC-1: NV xác nhận đơn COD PENDING → CONFIRMED (không đổi tồn)."""
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
async def test_uc21_status_history_times_customer_hides_cancel_note(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-21: timeline trạng thái; KH ẩn note hủy, NV thấy note."""
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
    reason = "Khách gọi điện đổi ý"
    await service.cancel_order_by_employee(
        db,
        employee_key=demo.employee_key,
        order_code=order.order_code,
        reason=reason,
        inventory=inv,
    )

    customer = await service.get_customer_order(
        db, account_key=demo.customer_key, order_code=order.order_code
    )
    assert len(customer.status_history) >= 3
    assert customer.status_label == "Đã hủy"
    assert customer.status_history[0].to_status == "PENDING"
    assert customer.status_history[0].event_label == "Chưa xử lý"
    assert customer.status_history[0].changed_at is not None
    confirmed_rows = [h for h in customer.status_history if h.to_status == "CONFIRMED"]
    assert confirmed_rows
    assert confirmed_rows[0].event_label == "Đã xác nhận"
    cancel_rows = [h for h in customer.status_history if h.to_status == "CANCELLED"]
    assert cancel_rows
    assert cancel_rows[-1].event_label == "Đã hủy"
    assert all(h.note is None for h in customer.status_history)

    staff = await service.get_staff_order(db, order_code=order.order_code)
    staff_cancel = [h for h in staff.status_history if h.to_status == "CANCELLED"]
    assert staff_cancel
    assert staff_cancel[-1].event_label == "Đã hủy"
    assert staff_cancel[-1].note == reason


@pytest.mark.asyncio
async def test_uc23_ac3_reject_unpaid_qr_order(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-23 AC-3: không xác nhận đơn QR còn UNPAID."""
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
