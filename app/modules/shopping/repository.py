"""Tầng Repository của module shopping: SQLModel ORM trên schema `shopping`.

Mỗi hàm gắn comment UC phía trên (UC-18 giỏ / gộp; UC-38 wishlist; UC-19/20 xóa dòng đã đặt).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from app.modules.shopping.models import (
    Cart,
    CartItem,
    CartMergeRequest,
    Wishlist,
    WishlistItem,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


# UC-18 — lấy cart_key theo account (giỏ đã tạo cùng tài khoản KH).
async def get_cart_key(db: AsyncSession, account_key: UUID) -> UUID | None:
    result = await db.exec(
        select(Cart.cart_key).where(Cart.cart_account_key == account_key)
    )
    return result.first()


# UC-18 Main Flow / AC-1–AC-4 / AC-7–AC-8 — liệt kê dòng giỏ (variant + qty).
async def list_cart_items(
    db: AsyncSession, cart_key: UUID
) -> list[tuple[UUID, UUID, int]]:
    result = await db.exec(
        select(CartItem)
        .where(CartItem.cart_item_cart_key == cart_key)
        .order_by(col(CartItem.cart_item_key))
    )
    items = result.all()
    return [
        (item.cart_item_key, item.cart_item_variant_key, item.cart_item_quantity)
        for item in items
    ]


# UC-18 AC-2 / AC-3 — đọc số lượng dòng biến thể (cộng dồn / kiểm tra tồn).
async def get_cart_item_quantity(
    db: AsyncSession, cart_key: UUID, variant_key: UUID
) -> tuple[UUID, int] | None:
    result = await db.exec(
        select(CartItem).where(
            CartItem.cart_item_cart_key == cart_key,
            CartItem.cart_item_variant_key == variant_key,
        )
    )
    item = result.first()
    if item is None:
        return None
    return item.cart_item_key, item.cart_item_quantity


# UC-18 AC-1 — thêm dòng biến thể mới vào giỏ.
async def insert_cart_item(
    db: AsyncSession, cart_key: UUID, variant_key: UUID, quantity: int
) -> int:
    item = CartItem(
        cart_item_cart_key=cart_key,
        cart_item_variant_key=variant_key,
        cart_item_quantity=quantity,
    )
    db.add(item)
    await db.flush()
    return item.cart_item_quantity


# UC-18 AC-2 / AC-3 / AC-6 / AC-9 — cập nhật số lượng dòng (cộng dồn / gộp / sửa SL).
async def update_cart_item_quantity(
    db: AsyncSession, cart_item_key: UUID, quantity: int
) -> int:
    result = await db.exec(
        select(CartItem).where(CartItem.cart_item_key == cart_item_key)
    )
    item = result.one()
    item.cart_item_quantity = quantity
    db.add(item)
    await db.flush()
    return item.cart_item_quantity


# UC-18 AC-4 — xóa một dòng biến thể khỏi giỏ.
async def delete_cart_item(
    db: AsyncSession, cart_key: UUID, variant_key: UUID
) -> bool:
    result = await db.exec(
        select(CartItem).where(
            CartItem.cart_item_cart_key == cart_key,
            CartItem.cart_item_variant_key == variant_key,
        )
    )
    item = result.first()
    if item is None:
        return False
    await db.delete(item)
    await db.flush()
    return True


# UC-19 / UC-20 — xóa các biến thể đã đặt khỏi giỏ sau khi tạo đơn.
async def delete_cart_items_by_variants(
    db: AsyncSession, cart_key: UUID, variant_keys: list[UUID]
) -> None:
    if not variant_keys:
        return
    result = await db.exec(
        select(CartItem).where(
            CartItem.cart_item_cart_key == cart_key,
            col(CartItem.cart_item_variant_key).in_(variant_keys),
        )
    )
    for item in result.all():
        await db.delete(item)
    await db.flush()


# UC-01 / UC-06 / UC-18 — tạo giỏ khi tạo tài khoản Khách hàng (không tạo lúc thêm SP).
async def create_cart(db: AsyncSession, account_key: UUID) -> UUID:
    cart = Cart(cart_account_key=account_key)
    db.add(cart)
    await db.flush()
    return cart.cart_key


# UC-01 / UC-06 / UC-38 — tạo wishlist cùng tài khoản Khách hàng.
async def create_wishlist(db: AsyncSession, account_key: UUID) -> UUID:
    wishlist = Wishlist(wishlist_account_key=account_key)
    db.add(wishlist)
    await db.flush()
    return wishlist.wishlist_key


# UC-38 — lấy wishlist_key theo account.
async def get_wishlist_key(db: AsyncSession, account_key: UUID) -> UUID | None:
    result = await db.exec(
        select(Wishlist.wishlist_key).where(
            Wishlist.wishlist_account_key == account_key
        )
    )
    return result.first()


# UC-38 AC-1 / AC-4 — thêm sản phẩm vào wishlist (unique; False nếu đã có).
async def insert_wishlist_item(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    """True nếu thêm mới; False nếu đã có (unique + savepoint, chống race)."""
    if await wishlist_has_product(db, wishlist_key, product_key):
        return False
    try:
        async with db.begin_nested():
            db.add(
                WishlistItem(
                    wishlist_item_wishlist_key=wishlist_key,
                    wishlist_item_product_key=product_key,
                )
            )
            await db.flush()
        return True
    except IntegrityError:
        return False


# UC-38 AC-2 — xóa sản phẩm khỏi wishlist.
async def delete_wishlist_item(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    result = await db.exec(
        select(WishlistItem).where(
            WishlistItem.wishlist_item_wishlist_key == wishlist_key,
            WishlistItem.wishlist_item_product_key == product_key,
        )
    )
    item = result.first()
    if item is None:
        return False
    await db.delete(item)
    await db.flush()
    return True


# UC-38 AC-6 — đếm số mục wishlist (empty / total).
async def count_wishlist_items(db: AsyncSession, wishlist_key: UUID) -> int:
    result = await db.exec(
        select(func.count())
        .select_from(WishlistItem)
        .where(WishlistItem.wishlist_item_wishlist_key == wishlist_key)
    )
    return int(result.one())


# UC-38 AC-3 — liệt kê product_key (mới nhất trước, phân trang).
async def list_wishlist_product_keys(
    db: AsyncSession, wishlist_key: UUID, *, limit: int, offset: int
) -> list[UUID]:
    result = await db.exec(
        select(WishlistItem.wishlist_item_product_key)
        .where(WishlistItem.wishlist_item_wishlist_key == wishlist_key)
        .order_by(
            col(WishlistItem.wishlist_item_added_at).desc(),
            col(WishlistItem.wishlist_item_key).desc(),
        )
        .offset(offset)
        .limit(limit)
    )
    return list(result.all())


# UC-38 AC-1 / AC-4 — kiểm tra sản phẩm đã có trong wishlist.
async def wishlist_has_product(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    result = await db.exec(
        select(WishlistItem.wishlist_item_key).where(
            WishlistItem.wishlist_item_wishlist_key == wishlist_key,
            WishlistItem.wishlist_item_product_key == product_key,
        )
    )
    return result.first() is not None


# UC-18 AC-10 / AC-11 — đọc payload_hash của mã gộp đã xử lý.
async def get_merge_payload_hash(
    db: AsyncSession, account_key: UUID, merge_id: str
) -> str | None:
    result = await db.exec(
        select(CartMergeRequest.cart_merge_request_payload_hash).where(
            CartMergeRequest.cart_merge_request_account_key == account_key,
            CartMergeRequest.cart_merge_request_id == merge_id,
        )
    )
    return result.first()


# UC-18 AC-10 / AC-11 / E6 — lưu dấu đã xử lý mã gộp (một lần; race → False).
async def insert_merge_request(
    db: AsyncSession, account_key: UUID, merge_id: str, payload_hash: str
) -> bool:
    """True nếu đây là lần đầu lưu mã gộp; False nếu mã đã tồn tại (race AC-11)."""
    existing = await get_merge_payload_hash(db, account_key, merge_id)
    if existing is not None:
        return False
    try:
        async with db.begin_nested():
            db.add(
                CartMergeRequest(
                    cart_merge_request_account_key=account_key,
                    cart_merge_request_id=merge_id,
                    cart_merge_request_payload_hash=payload_hash,
                )
            )
            await db.flush()
        return True
    except IntegrityError:
        return False
