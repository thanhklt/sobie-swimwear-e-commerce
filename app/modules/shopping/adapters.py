"""Adapter tạm [GD] cho UI thử shopping — đọc seed catalog/inventory/identity.

Thay bằng service công khai của catalog / inventory / identity khi teammate sẵn sàng.
Shopping service vẫn chỉ nhận protocol; không gọi SQL module khác trong repository.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text

from app.modules.shopping.dependencies import ProductCardData

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

DEMO_EMAIL = "khachhang@example.com"


async def get_demo_account_key(db: AsyncSession) -> UUID:
    result = await db.exec(
        text(
            "SELECT account_key FROM identity.account WHERE account_email = :email"
        ),
        params={"email": DEMO_EMAIL},
    )
    row = result.first()
    if row is None:
        raise RuntimeError(f"Không tìm thấy tài khoản demo {DEMO_EMAIL}")
    return UUID(str(row[0]))


async def list_seed_variants(db: AsyncSession) -> list[dict]:
    result = await db.exec(
        text(
            """
            SELECT v.variant_key, v.variant_id, v.variant_sell_price,
                   c.color_name, s.size_name, p.product_name,
                   COALESCE(st.stock_quantity, 0) AS stock_quantity,
                   p.product_status
            FROM catalog.variant v
            JOIN catalog.product p ON p.product_key = v.variant_product_key
            JOIN catalog.color c ON c.color_key = v.variant_color_key
            JOIN catalog.size s ON s.size_key = v.variant_size_key
            LEFT JOIN inventory.stock st ON st.stock_variant_key = v.variant_key
            ORDER BY v.variant_id
            """
        )
    )
    rows = result.mappings().all()
    return [
        {
            "variant_key": UUID(str(r["variant_key"])),
            "variant_id": r["variant_id"],
            "label": f'{r["product_name"]} — {r["color_name"]} / {r["size_name"]}',
            "price": Decimal(r["variant_sell_price"]),
            "stock": int(r["stock_quantity"]),
            "sellable": r["product_status"] == "ACTIVE",
        }
        for r in rows
    ]


async def list_seed_products(db: AsyncSession) -> list[dict]:
    result = await db.exec(
        text(
            """
            SELECT p.product_key, p.product_id, p.product_name, p.product_status,
                   MIN(v.variant_sell_price) AS min_price,
                   (
                     SELECT g.gallery_url
                     FROM catalog.gallery g
                     WHERE g.gallery_product_key = p.product_key
                     ORDER BY g.gallery_order_no
                     LIMIT 1
                   ) AS image_url
            FROM catalog.product p
            JOIN catalog.variant v ON v.variant_product_key = p.product_key
            GROUP BY p.product_key, p.product_id, p.product_name, p.product_status
            ORDER BY p.product_id
            """
        )
    )
    rows = result.mappings().all()
    return [
        {
            "product_key": UUID(str(r["product_key"])),
            "product_id": r["product_id"],
            "name": r["product_name"],
            "image_url": r["image_url"],
            "min_price": Decimal(r["min_price"]),
            "is_active": r["product_status"] == "ACTIVE",
        }
        for r in rows
    ]


class SeedAvailability:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        result = await self._db.exec(
            text(
                """
                SELECT COALESCE(stock_quantity, 0)
                FROM inventory.stock
                WHERE stock_variant_key = :variant_key
                """
            ),
            params={"variant_key": variant_key},
        )
        row = result.first()
        return int(row[0]) if row else 0

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        result = await self._db.exec(
            text(
                """
                SELECT p.product_status
                FROM catalog.variant v
                JOIN catalog.product p ON p.product_key = v.variant_product_key
                WHERE v.variant_key = :variant_key
                """
            ),
            params={"variant_key": variant_key},
        )
        row = result.first()
        return bool(row and row[0] == "ACTIVE")


class SeedPricing:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_current_unit_price(self, variant_key: UUID) -> Decimal:
        result = await self._db.exec(
            text(
                """
                SELECT variant_sell_price
                FROM catalog.variant
                WHERE variant_key = :variant_key
                """
            ),
            params={"variant_key": variant_key},
        )
        row = result.one()
        return Decimal(row[0])


class SeedProductCatalog:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def product_exists(self, product_key: UUID) -> bool:
        result = await self._db.exec(
            text(
                "SELECT 1 FROM catalog.product WHERE product_key = :product_key"
            ),
            params={"product_key": product_key},
        )
        return result.first() is not None

    async def is_product_active(self, product_key: UUID) -> bool:
        result = await self._db.exec(
            text(
                """
                SELECT product_status FROM catalog.product
                WHERE product_key = :product_key
                """
            ),
            params={"product_key": product_key},
        )
        row = result.first()
        return bool(row and row[0] == "ACTIVE")

    async def get_product_card(self, product_key: UUID) -> ProductCardData:
        result = await self._db.exec(
            text(
                """
                SELECT p.product_key, p.product_id, p.product_name, p.product_status,
                       MIN(v.variant_sell_price) AS min_price,
                       (
                         SELECT g.gallery_url
                         FROM catalog.gallery g
                         WHERE g.gallery_product_key = p.product_key
                         ORDER BY g.gallery_order_no
                         LIMIT 1
                       ) AS image_url
                FROM catalog.product p
                JOIN catalog.variant v ON v.variant_product_key = p.product_key
                WHERE p.product_key = :product_key
                GROUP BY p.product_key, p.product_id, p.product_name, p.product_status
                """
            ),
            params={"product_key": product_key},
        )
        row = result.mappings().one()
        return ProductCardData(
            product_key=UUID(str(row["product_key"])),
            product_id=row["product_id"],
            name=row["product_name"],
            image_url=row["image_url"],
            min_price=Decimal(row["min_price"]),
            is_active=row["product_status"] == "ACTIVE",
        )


async def variant_labels(db: AsyncSession, variant_keys: list[UUID]) -> dict[UUID, str]:
    if not variant_keys:
        return {}
    # Load all seed variants once and filter — đủ cho UI demo
    all_variants = await list_seed_variants(db)
    wanted = set(variant_keys)
    return {
        v["variant_key"]: v["label"]
        for v in all_variants
        if v["variant_key"] in wanted
    }
