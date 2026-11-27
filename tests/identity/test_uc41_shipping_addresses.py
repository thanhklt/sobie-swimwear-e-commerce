"""UC-41 — sổ địa chỉ giao hàng."""

from __future__ import annotations

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.identity import service
from app.modules.identity.exceptions import (
    InvalidShippingAddressError,
    ShippingAddressNotFoundError,
)
from app.modules.identity.schemas import ShippingAddressCreate
from tests.identity.conftest import DemoIds


@pytest.mark.asyncio
async def test_uc41_ac1_first_address_is_default(
    db: AsyncSession, demo: DemoIds, reset_addresses: None
) -> None:
    """UC-41 AC-1: địa chỉ đầu tiên thành mặc định (+ mirror account)."""
    addrs = await service.list_shipping_addresses(db, demo.account_key)
    assert len(addrs) == 1
    assert addrs[0].is_default is True
    default = await service.get_default_shipping_address(db, demo.account_key)
    assert default is not None
    assert default.shipping_address_key == addrs[0].shipping_address_key


@pytest.mark.asyncio
async def test_uc41_ac2_second_address_not_default(
    db: AsyncSession, demo: DemoIds, reset_addresses: None
) -> None:
    """UC-41 AC-2: thêm địa chỉ thứ hai không đổi mặc định."""
    first = await service.get_default_shipping_address(db, demo.account_key)
    assert first is not None
    second = await service.add_shipping_address(
        db,
        account_key=demo.account_key,
        data=ShippingAddressCreate(
            name="Nhà 2",
            phone="0900000003",
            house_number="10 Nguyễn Huệ",
            ward="Phường Bến Nghé",
            city="TP. Hồ Chí Minh",
            country="Việt Nam",
        ),
    )
    assert second.is_default is False
    addrs = await service.list_shipping_addresses(db, demo.account_key)
    assert len(addrs) == 2
    default = await service.get_default_shipping_address(db, demo.account_key)
    assert default is not None
    assert default.shipping_address_key == first.shipping_address_key


@pytest.mark.asyncio
async def test_uc41_ac3_set_default_switches(
    db: AsyncSession, demo: DemoIds, reset_addresses: None
) -> None:
    """UC-41 AC-3: đặt B làm mặc định → A mất mặc định; mirror khớp B."""
    first = await service.get_default_shipping_address(db, demo.account_key)
    assert first is not None
    second = await service.add_shipping_address(
        db,
        account_key=demo.account_key,
        data=ShippingAddressCreate(
            name="Công ty",
            phone="0900000003",
            house_number="1 Lê Lợi",
            ward="Phường Bến Thành",
            city="TP. Hồ Chí Minh",
            country="Việt Nam",
        ),
    )
    updated = await service.set_default_shipping_address(
        db, account_key=demo.account_key, address_key=second.shipping_address_key
    )
    assert updated.is_default is True
    assert updated.shipping_address_key == second.shipping_address_key

    addrs = await service.list_shipping_addresses(db, demo.account_key)
    defaults = [a for a in addrs if a.is_default]
    assert len(defaults) == 1
    assert defaults[0].shipping_address_key == second.shipping_address_key
    assert all(
        not a.is_default
        for a in addrs
        if a.shipping_address_key != second.shipping_address_key
    )


@pytest.mark.asyncio
async def test_uc41_reject_empty_field(
    db: AsyncSession, demo: DemoIds, reset_addresses: None
) -> None:
    """UC-41 E1: thiếu trường bắt buộc → không lưu."""
    with pytest.raises(InvalidShippingAddressError):
        await service.add_shipping_address(
            db,
            account_key=demo.account_key,
            data=ShippingAddressCreate(
                name="A",
                phone="090",
                house_number="",
                ward="P",
                city="C",
                country="Việt Nam",
            ),
        )


@pytest.mark.asyncio
async def test_uc41_set_default_unknown_address(
    db: AsyncSession, demo: DemoIds, reset_addresses: None
) -> None:
    """UC-41 E2: đặt mặc định địa chỉ không thuộc tài khoản → từ chối."""
    from uuid import uuid4

    with pytest.raises(ShippingAddressNotFoundError):
        await service.set_default_shipping_address(
            db, account_key=demo.account_key, address_key=uuid4()
        )
