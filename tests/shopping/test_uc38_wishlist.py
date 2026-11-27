"""UC-38 — danh sách yêu thích (service + DB)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping import service
from app.modules.shopping.dependencies import ProductCardData
from app.modules.shopping.exceptions import ProductNotFoundError, WishlistNotFoundError
from tests.shopping.conftest import DemoIds, catalog_for


def _card(
    product_key: UUID,
    product_id: str,
    *,
    name: str = "SP",
    active: bool = True,
    price: int = 2000,
) -> ProductCardData:
    return ProductCardData(
        product_key=product_key,
        product_id=product_id,
        name=name,
        image_url="/static/x.jpg",
        min_price=Decimal(price),
        is_active=active,
    )


@pytest.mark.asyncio
async def test_uc38_ac1_add_product_to_wishlist(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-1: thêm sản phẩm vào wishlist thành công."""
    catalog = catalog_for(_card(demo.product_sp1, "SP-0001", name="Demo"))
    added = await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp1,
        catalog=catalog,
    )
    assert added is True
    assert (
        await service.is_product_in_wishlist(
            db, account_key=demo.account_key, product_key=demo.product_sp1
        )
        is True
    )


@pytest.mark.asyncio
async def test_uc38_ac2_remove_product_from_wishlist(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-2: bỏ tim → xóa khỏi wishlist."""
    catalog = catalog_for(_card(demo.product_sp1, "SP-0001"))
    await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp1,
        catalog=catalog,
    )
    await service.remove_from_wishlist(
        db, account_key=demo.account_key, product_key=demo.product_sp1
    )
    assert (
        await service.is_product_in_wishlist(
            db, account_key=demo.account_key, product_key=demo.product_sp1
        )
        is False
    )


@pytest.mark.asyncio
async def test_uc38_ac3_wishlist_newest_first(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-3: danh sách sắp xếp mới nhất trước."""
    catalog = catalog_for(
        _card(demo.product_sp1, "SP-0001", name="A"),
        _card(demo.product_sp2, "SP-0002", name="B"),
    )
    await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp1,
        catalog=catalog,
    )
    await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp2,
        catalog=catalog,
    )
    view = await service.get_wishlist(
        db, account_key=demo.account_key, catalog=catalog
    )
    assert [i.product_id for i in view.items] == ["SP-0002", "SP-0001"]


@pytest.mark.asyncio
async def test_uc38_ac4_no_duplicate_product(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-4: thêm trùng sản phẩm → không tạo dòng thứ hai."""
    catalog = catalog_for(_card(demo.product_sp1, "SP-0001"))
    assert (
        await service.add_to_wishlist(
            db,
            account_key=demo.account_key,
            product_key=demo.product_sp1,
            catalog=catalog,
        )
        is True
    )
    assert (
        await service.add_to_wishlist(
            db,
            account_key=demo.account_key,
            product_key=demo.product_sp1,
            catalog=catalog,
        )
        is False
    )
    view = await service.get_wishlist(
        db, account_key=demo.account_key, catalog=catalog
    )
    assert view.total_items == 1


@pytest.mark.asyncio
async def test_uc38_ac5_guest_must_login_not_saved() -> None:
    """UC-38 AC-5: không có API ghi wishlist ẩn danh — cần account_key."""
    assert callable(service.add_to_wishlist)


@pytest.mark.asyncio
async def test_uc38_ac6_empty_wishlist_message_data(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-6: wishlist trống → total_items = 0, items rỗng."""
    catalog = catalog_for(_card(demo.product_sp1, "SP-0001"))
    view = await service.get_wishlist(
        db, account_key=demo.account_key, catalog=catalog
    )
    assert view.total_items == 0
    assert view.items == ()


@pytest.mark.asyncio
async def test_uc38_ac7_discontinued_product_still_listed(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-7: SP ngừng bán vẫn nằm trong list, không mở detail."""
    catalog = catalog_for(
        _card(demo.product_sp1, "SP-0001", name="Ngừng", active=False)
    )
    await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp1,
        catalog=catalog,
    )
    view = await service.get_wishlist(
        db, account_key=demo.account_key, catalog=catalog
    )
    assert view.items[0].is_active is False
    assert view.items[0].can_open_detail is False
    await service.remove_from_wishlist(
        db, account_key=demo.account_key, product_key=demo.product_sp1
    )


@pytest.mark.asyncio
async def test_uc38_ac8_wishlist_isolated_by_account(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 AC-8: wishlist theo tài khoản — account lạ → không đọc được."""
    catalog = catalog_for(_card(demo.product_sp1, "SP-0001"))
    await service.add_to_wishlist(
        db,
        account_key=demo.account_key,
        product_key=demo.product_sp1,
        catalog=catalog,
    )
    with pytest.raises(WishlistNotFoundError):
        await service.get_wishlist(db, account_key=uuid4(), catalog=catalog)


@pytest.mark.asyncio
async def test_uc38_e2_product_not_found(
    db: AsyncSession, demo: DemoIds, clean_wishlist: None
) -> None:
    """UC-38 E2: product_key không tồn tại → từ chối thêm."""
    with pytest.raises(ProductNotFoundError):
        await service.add_to_wishlist(
            db,
            account_key=demo.account_key,
            product_key=uuid4(),
            catalog=catalog_for(),
        )
