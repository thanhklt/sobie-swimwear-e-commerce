"""UC-19 AC-12 / AC-13 — checkout dùng sổ địa chỉ (UC-41)."""

from __future__ import annotations

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.identity import repository as identity_repository
from app.modules.identity import service as identity_service
from app.modules.identity.schemas import ShippingAddressCreate
from app.modules.ordering import service
from app.modules.ordering.schemas import ShippingInfo
from tests.ordering.conftest import DemoIds, prepare_cart, sample_shipping


async def _delete_address(db: AsyncSession, *, account_key, address_key) -> None:
    row = await identity_repository.get_shipping_address(
        db, account_key=account_key, address_key=address_key
    )
    if row is not None:
        await db.delete(row)
        await db.commit()


@pytest.mark.asyncio
async def test_uc19_ac12_prefill_uses_default_address(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-12: checkout prefill theo địa chỉ mặc định (A), không lấy B."""
    default = await identity_service.get_default_shipping_address(db, demo.customer_key)
    assert default is not None
    sample = sample_shipping()
    assert default.name == sample.name
    assert default.house_number == sample.house_number
    assert default.ward == sample.ward
    assert default.city == sample.city
    assert default.is_default is True

    second = await identity_service.add_shipping_address(
        db,
        account_key=demo.customer_key,
        data=ShippingAddressCreate(
            name="Nhà phụ",
            phone="0900000003",
            house_number="99 Nguyễn Trãi",
            ward="Phường Nguyễn Cư Trinh",
            city="TP. Hồ Chí Minh",
            country="Việt Nam",
        ),
    )
    try:
        assert second.is_default is False
        still_default = await identity_service.get_default_shipping_address(
            db, demo.customer_key
        )
        assert still_default is not None
        assert still_default.shipping_address_key == default.shipping_address_key
    finally:
        await _delete_address(
            db,
            account_key=demo.customer_key,
            address_key=second.shipping_address_key,
        )


@pytest.mark.asyncio
async def test_uc19_ac13_add_at_checkout_persists_and_snapshots(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    """UC-19 AC-13 (+ UC-41 AC-4): thêm địa chỉ tại checkout lưu sổ; snapshot vào đơn."""
    created = await identity_service.add_shipping_address(
        db,
        account_key=demo.customer_key,
        data=ShippingAddressCreate(
            name="Công ty Sobie",
            phone="0900111222",
            house_number="1 Lê Lợi",
            ward="Phường Bến Thành",
            city="TP. Hồ Chí Minh",
            country="Việt Nam",
        ),
    )
    try:
        listed_before = await identity_service.list_shipping_addresses(
            db, demo.customer_key
        )
        assert created.shipping_address_key in {
            a.shipping_address_key for a in listed_before
        }

        inv, pricing = await prepare_cart(db, demo, qty=1, stock=5)
        order = await service.place_cod_order(
            db,
            account_key=demo.customer_key,
            shipping=ShippingInfo(
                name=created.name,
                phone=created.phone,
                house_number=created.house_number,
                ward=created.ward,
                city=created.city,
                country=created.country,
            ),
            inventory=inv,
            pricing=pricing,
        )
        assert order.order_customer_name == "Công ty Sobie"
        assert order.order_customer_house_number == "1 Lê Lợi"
        assert order.order_customer_ward == "Phường Bến Thành"

        listed_after = await identity_service.list_shipping_addresses(
            db, demo.customer_key
        )
        assert created.shipping_address_key in {
            a.shipping_address_key for a in listed_after
        }
    finally:
        await _delete_address(
            db,
            account_key=demo.customer_key,
            address_key=created.shipping_address_key,
        )
