"""Tầng Repository của module shopping: chỉ truy vấn bảng schema `shopping`."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import bindparam, text

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

_GET_CART_KEY = text(
    """
    SELECT cart_key
    FROM shopping.cart
    WHERE cart_account_key = :account_key
    """
)

_LIST_CART_ITEMS = text(
    """
    SELECT cart_item_key, cart_item_variant_key, cart_item_quantity
    FROM shopping.cart_item
    WHERE cart_item_cart_key = :cart_key
    ORDER BY cart_item_key
    """
)

_GET_CART_ITEM_BY_VARIANT = text(
    """
    SELECT cart_item_key, cart_item_quantity
    FROM shopping.cart_item
    WHERE cart_item_cart_key = :cart_key
      AND cart_item_variant_key = :variant_key
    """
)

_INSERT_CART_ITEM = text(
    """
    INSERT INTO shopping.cart_item (
        cart_item_cart_key, cart_item_variant_key, cart_item_quantity
    )
    VALUES (:cart_key, :variant_key, :quantity)
    RETURNING cart_item_key, cart_item_quantity
    """
)

_UPDATE_CART_ITEM_QTY = text(
    """
    UPDATE shopping.cart_item
    SET cart_item_quantity = :quantity
    WHERE cart_item_key = :cart_item_key
    RETURNING cart_item_key, cart_item_quantity
    """
)

_DELETE_CART_ITEM = text(
    """
    DELETE FROM shopping.cart_item
    WHERE cart_item_cart_key = :cart_key
      AND cart_item_variant_key = :variant_key
    RETURNING cart_item_key
    """
)

_DELETE_CART_ITEMS_BY_VARIANTS = text(
    """
    DELETE FROM shopping.cart_item
    WHERE cart_item_cart_key = :cart_key
      AND cart_item_variant_key IN :variant_keys
    """
).bindparams(bindparam("variant_keys", expanding=True))

_INSERT_CART = text(
    """
    INSERT INTO shopping.cart (cart_account_key)
    VALUES (:account_key)
    RETURNING cart_key
    """
)

_INSERT_WISHLIST = text(
    """
    INSERT INTO shopping.wishlist (wishlist_account_key)
    VALUES (:account_key)
    RETURNING wishlist_key
    """
)

_GET_WISHLIST_KEY = text(
    """
    SELECT wishlist_key
    FROM shopping.wishlist
    WHERE wishlist_account_key = :account_key
    """
)

_INSERT_WISHLIST_ITEM = text(
    """
    INSERT INTO shopping.wishlist_item (
        wishlist_item_wishlist_key, wishlist_item_product_key
    )
    VALUES (:wishlist_key, :product_key)
    ON CONFLICT ON CONSTRAINT wishlist_item_wishlist_product_uq DO NOTHING
    RETURNING wishlist_item_key
    """
)

_DELETE_WISHLIST_ITEM = text(
    """
    DELETE FROM shopping.wishlist_item
    WHERE wishlist_item_wishlist_key = :wishlist_key
      AND wishlist_item_product_key = :product_key
    RETURNING wishlist_item_key
    """
)

_COUNT_WISHLIST_ITEMS = text(
    """
    SELECT count(*)::int AS total
    FROM shopping.wishlist_item
    WHERE wishlist_item_wishlist_key = :wishlist_key
    """
)

_LIST_WISHLIST_ITEMS = text(
    """
    SELECT wishlist_item_product_key
    FROM shopping.wishlist_item
    WHERE wishlist_item_wishlist_key = :wishlist_key
    ORDER BY wishlist_item_added_at DESC, wishlist_item_key DESC
    LIMIT :limit OFFSET :offset
    """
)

_WISHLIST_HAS_PRODUCT = text(
    """
    SELECT 1
    FROM shopping.wishlist_item
    WHERE wishlist_item_wishlist_key = :wishlist_key
      AND wishlist_item_product_key = :product_key
    """
)

_GET_MERGE_REQUEST = text(
    """
    SELECT cart_merge_request_payload_hash
    FROM shopping.cart_merge_request
    WHERE cart_merge_request_account_key = :account_key
      AND cart_merge_request_id = :merge_id
    """
)

_INSERT_MERGE_REQUEST = text(
    """
    INSERT INTO shopping.cart_merge_request (
        cart_merge_request_account_key,
        cart_merge_request_id,
        cart_merge_request_payload_hash
    )
    VALUES (:account_key, :merge_id, :payload_hash)
    ON CONFLICT ON CONSTRAINT cart_merge_request_account_id_uq DO NOTHING
    RETURNING cart_merge_request_key
    """
)


async def get_cart_key(db: AsyncSession, account_key: UUID) -> UUID | None:
    result = await db.exec(_GET_CART_KEY, params={"account_key": account_key})
    row = result.first()
    return UUID(str(row[0])) if row else None


async def list_cart_items(
    db: AsyncSession, cart_key: UUID
) -> list[tuple[UUID, UUID, int]]:
    result = await db.exec(_LIST_CART_ITEMS, params={"cart_key": cart_key})
    return [
        (UUID(str(r[0])), UUID(str(r[1])), int(r[2])) for r in result.all()
    ]


async def get_cart_item_quantity(
    db: AsyncSession, cart_key: UUID, variant_key: UUID
) -> tuple[UUID, int] | None:
    result = await db.exec(
        _GET_CART_ITEM_BY_VARIANT,
        params={"cart_key": cart_key, "variant_key": variant_key},
    )
    row = result.first()
    if row is None:
        return None
    return UUID(str(row[0])), int(row[1])


async def insert_cart_item(
    db: AsyncSession, cart_key: UUID, variant_key: UUID, quantity: int
) -> int:
    result = await db.exec(
        _INSERT_CART_ITEM,
        params={
            "cart_key": cart_key,
            "variant_key": variant_key,
            "quantity": quantity,
        },
    )
    row = result.one()
    return int(row[1])


async def update_cart_item_quantity(
    db: AsyncSession, cart_item_key: UUID, quantity: int
) -> int:
    result = await db.exec(
        _UPDATE_CART_ITEM_QTY,
        params={"cart_item_key": cart_item_key, "quantity": quantity},
    )
    row = result.one()
    return int(row[1])


async def delete_cart_item(
    db: AsyncSession, cart_key: UUID, variant_key: UUID
) -> bool:
    result = await db.exec(
        _DELETE_CART_ITEM,
        params={"cart_key": cart_key, "variant_key": variant_key},
    )
    return result.first() is not None


async def delete_cart_items_by_variants(
    db: AsyncSession, cart_key: UUID, variant_keys: list[UUID]
) -> None:
    if not variant_keys:
        return
    await db.exec(
        _DELETE_CART_ITEMS_BY_VARIANTS,
        params={"cart_key": cart_key, "variant_keys": tuple(variant_keys)},
    )


async def create_cart(db: AsyncSession, account_key: UUID) -> UUID:
    result = await db.exec(_INSERT_CART, params={"account_key": account_key})
    return UUID(str(result.one()[0]))


async def create_wishlist(db: AsyncSession, account_key: UUID) -> UUID:
    result = await db.exec(_INSERT_WISHLIST, params={"account_key": account_key})
    return UUID(str(result.one()[0]))


async def get_wishlist_key(db: AsyncSession, account_key: UUID) -> UUID | None:
    result = await db.exec(_GET_WISHLIST_KEY, params={"account_key": account_key})
    row = result.first()
    return UUID(str(row[0])) if row else None


async def insert_wishlist_item(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    """True nếu thêm mới; False nếu đã có (ON CONFLICT DO NOTHING)."""
    result = await db.exec(
        _INSERT_WISHLIST_ITEM,
        params={"wishlist_key": wishlist_key, "product_key": product_key},
    )
    return result.first() is not None


async def delete_wishlist_item(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    result = await db.exec(
        _DELETE_WISHLIST_ITEM,
        params={"wishlist_key": wishlist_key, "product_key": product_key},
    )
    return result.first() is not None


async def count_wishlist_items(db: AsyncSession, wishlist_key: UUID) -> int:
    result = await db.exec(
        _COUNT_WISHLIST_ITEMS, params={"wishlist_key": wishlist_key}
    )
    return int(result.one()[0])


async def list_wishlist_product_keys(
    db: AsyncSession, wishlist_key: UUID, *, limit: int, offset: int
) -> list[UUID]:
    result = await db.exec(
        _LIST_WISHLIST_ITEMS,
        params={"wishlist_key": wishlist_key, "limit": limit, "offset": offset},
    )
    return [UUID(str(r[0])) for r in result.all()]


async def wishlist_has_product(
    db: AsyncSession, wishlist_key: UUID, product_key: UUID
) -> bool:
    result = await db.exec(
        _WISHLIST_HAS_PRODUCT,
        params={"wishlist_key": wishlist_key, "product_key": product_key},
    )
    return result.first() is not None


async def get_merge_payload_hash(
    db: AsyncSession, account_key: UUID, merge_id: str
) -> str | None:
    result = await db.exec(
        _GET_MERGE_REQUEST,
        params={"account_key": account_key, "merge_id": merge_id},
    )
    row = result.first()
    return str(row[0]) if row else None


async def insert_merge_request(
    db: AsyncSession, account_key: UUID, merge_id: str, payload_hash: str
) -> bool:
    """True nếu đây là lần đầu lưu mã gộp; False nếu mã đã tồn tại (race AC-11)."""
    result = await db.exec(
        _INSERT_MERGE_REQUEST,
        params={
            "account_key": account_key,
            "merge_id": merge_id,
            "payload_hash": payload_hash,
        },
    )
    return result.first() is not None
