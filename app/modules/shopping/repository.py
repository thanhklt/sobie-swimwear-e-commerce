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
from sqlalchemy.dialects.postgresql import JSONB

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


async def lock_cart(db, account_key):
    await db.execute(text("""
        INSERT INTO shopping.cart (cart_account_key) VALUES (:account_key)
        ON CONFLICT (cart_account_key) DO NOTHING
    """), {"account_key": account_key})
    return (await db.execute(text("""
        SELECT cart_key FROM shopping.cart WHERE cart_account_key = :account_key FOR UPDATE
    """), {"account_key": account_key})).scalar_one()


async def cart_quantities(db, account_key):
    rows = await db.execute(text("""
        SELECT cart_item_variant_key, cart_item_quantity
        FROM shopping.cart JOIN shopping.cart_item ON cart_item_cart_key = cart_key
        WHERE cart_account_key = :account_key ORDER BY cart_item_variant_key
    """), {"account_key": account_key})
    return dict(rows.all())


async def set_cart_quantity(db, cart_key, variant_key, quantity):
    await db.execute(text("""
        INSERT INTO shopping.cart_item (cart_item_cart_key, cart_item_variant_key, cart_item_quantity)
        VALUES (:cart_key, :variant_key, :quantity)
        ON CONFLICT (cart_item_cart_key, cart_item_variant_key)
        DO UPDATE SET cart_item_quantity = EXCLUDED.cart_item_quantity
    """), {"cart_key": cart_key, "variant_key": variant_key, "quantity": quantity})


async def find_cart_merge(db, cart_key, merge_key):
    rows = await db.execute(text("""
        SELECT payload_hash, result FROM shopping.cart_merge
        WHERE cart_key = :cart_key AND merge_key = :merge_key
    """), {"cart_key": cart_key, "merge_key": merge_key})
    return rows.one_or_none()


async def record_cart_merge(db, cart_key, merge_key, payload_hash, result):
    await db.execute(text("""
        INSERT INTO shopping.cart_merge (cart_key, merge_key, payload_hash, result)
        VALUES (:cart_key, :merge_key, :payload_hash, :result)
    """).bindparams(bindparam("result", type_=JSONB)), {
        "cart_key": cart_key, "merge_key": merge_key, "payload_hash": payload_hash, "result": result,
    })
