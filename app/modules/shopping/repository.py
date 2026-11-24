"""Tầng Repository của module shopping: truy vấn các bảng do module sở hữu:
- shopping.cart
- shopping.cart_item
- shopping.wishlist
- shopping.wishlist_item

Không truy vấn bảng của module khác.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Uuid, bindparam, text

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


_INSERT_CART = text(
    "INSERT INTO shopping.cart (cart_account_key) VALUES (:account_key)"
).bindparams(bindparam("account_key", type_=Uuid()))

_INSERT_WISHLIST = text(
    "INSERT INTO shopping.wishlist (wishlist_account_key) VALUES (:account_key)"
).bindparams(bindparam("account_key", type_=Uuid()))


async def insert_cart(db: "AsyncSession", *, account_key: UUID) -> None:
    await db.exec(_INSERT_CART, params={"account_key": account_key})


async def insert_wishlist(db: "AsyncSession", *, account_key: UUID) -> None:
    await db.exec(_INSERT_WISHLIST, params={"account_key": account_key})
