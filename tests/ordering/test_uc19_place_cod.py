"""UC-19 — đặt hàng COD (service + DB)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import repository, service
from app.modules.ordering.exceptions import (
    EmptyCartError,
    InsufficientStockError,
    MissingShippingInfoError,
    PriceChangedError,
)
from app.modules.ordering.schemas import ShippingInfo
from app.modules.shopping import service as shopping_service
from tests.ordering.conftest import (
    DemoIds,
    get_stock,
    prepare_cart,
    sample_shipping,
    set_stock,
)


@pytest.mark.asyncio
async def test_uc19_ac1_create_cod_order(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-1: đặt COD thành công — PENDING, trừ tồn, xóa giỏ, history."""
    inv, pricing = await prepare_cart(db, demo, qty=2, stock=5)
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
    )
    assert order.order_status == "PENDING"
    assert await get_stock(db, demo.variant_do_m) == 3
    cart = await shopping_service.list_cart_variant_quantities(db, demo.customer_key)
    assert demo.variant_do_m not in cart

    hist = await repository.list_status_history(db, order.order_key)
    assert len(hist) == 1
    assert hist[0].order_status_history_from_value is None
    assert hist[0].order_status_history_to_value == "PENDING"
    assert hist[0].order_status_history_source == "CUSTOMER"

    pay_name = await repository.payment_name_of(db, order.order_payment_key)
    assert pay_name == "COD"


@pytest.mark.asyncio
async def test_uc19_ac2_total_formula(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-2: tổng = tạm tính − giảm + ship (2×300000 + 12000 = 612000)."""
    inv, pricing = await prepare_cart(db, demo, qty=2, stock=10)
    quote = await service.build_quote(
        db, account_key=demo.customer_key, inventory=inv, pricing=pricing
    )
    assert quote.subtotal == Decimal("600000")
    assert quote.discount_amount == Decimal("0")
    assert quote.shipping_fee == Decimal("12000")
    assert quote.total_price == Decimal("612000")
    order = await service.place_cod_order(
        db,
        account_key=demo.customer_key,
        shipping=sample_shipping(),
        inventory=inv,
        pricing=pricing,
        expected_total=quote.total_price,
    )
    assert order.order_total_price == Decimal("612000")


@pytest.mark.asyncio
async def test_uc19_ac5_reject_when_stock_insufficient(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-5 / E1: hết hàng lúc xác nhận → không tạo đơn, không trừ tồn."""
    inv, pricing = await prepare_cart(db, demo, qty=2, stock=5)
    await set_stock(db, demo.variant_do_m, 1)
    with pytest.raises(InsufficientStockError):
        await service.place_cod_order(
            db,
            account_key=demo.customer_key,
            shipping=sample_shipping(),
            inventory=inv,
            pricing=pricing,
        )
    assert await get_stock(db, demo.variant_do_m) == 1
    cart = await shopping_service.list_cart_variant_quantities(db, demo.customer_key)
    assert cart[demo.variant_do_m] == 2


@pytest.mark.asyncio
async def test_uc19_ac7_missing_phone(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-7 / E3: thiếu thông tin nhận hàng → không tạo đơn."""
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    bad = ShippingInfo(
        name="A",
        phone="",
        house_number="1",
        ward="W",
        city="C",
        country="VN",
    )
    with pytest.raises(MissingShippingInfoError) as exc:
        await service.place_cod_order(
            db,
            account_key=demo.customer_key,
            shipping=bad,
            inventory=inv,
            pricing=pricing,
        )
    assert "số điện thoại" in exc.value.message


@pytest.mark.asyncio
async def test_uc19_ac9_price_changed_requires_reconfirm(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-9 / E4: tổng đổi so với expected_total → yêu cầu xác nhận lại."""
    inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
    with pytest.raises(PriceChangedError):
        await service.place_cod_order(
            db,
            account_key=demo.customer_key,
            shipping=sample_shipping(),
            inventory=inv,
            pricing=pricing,
            expected_total=Decimal("1"),
        )
    assert await get_stock(db, demo.variant_do_m) == 5


@pytest.mark.asyncio
async def test_uc19_empty_cart(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 Preconditions: giỏ trống → không đặt hàng."""
    from app.modules.ordering.adapters import DbCatalogPricing, DbInventoryGateway

    with pytest.raises(EmptyCartError):
        await service.place_cod_order(
            db,
            account_key=demo.customer_key,
            shipping=sample_shipping(),
            inventory=DbInventoryGateway(db),
            pricing=DbCatalogPricing(db),
        )
