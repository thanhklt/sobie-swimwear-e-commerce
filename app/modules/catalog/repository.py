"""Tầng Repository của module catalog: truy vấn các bảng do module sở hữu:
- catalog.category
- catalog.collection
- catalog.gender
- catalog.size
- catalog.color
- catalog.product
- catalog.product_collection
- catalog.variant
- catalog.gallery

Không truy vấn bảng của module khác. Hiện triển khai các truy vấn phục vụ inventory.
"""

from uuid import UUID

from sqlalchemy import bindparam, text
from sqlmodel.ext.asyncio.session import AsyncSession

_VARIANTS = """
SELECT v.variant_key, v.variant_id, v.variant_product_key,
       p.product_name, p.product_category_key AS category_key,
       c.color_name, s.size_name
FROM catalog.variant AS v
JOIN catalog.product AS p ON p.product_key = v.variant_product_key
JOIN catalog.color AS c ON c.color_key = v.variant_color_key
JOIN catalog.size AS s ON s.size_key = v.variant_size_key
"""


async def get_inventory_variants(db: AsyncSession, variant_keys: list[UUID], *, lock: bool = False) -> list[dict]:
    if not variant_keys:
        return []
    params = {"keys": list(set(variant_keys))}
    if lock:
        # Every parent is locked before any variant; never lock taxonomy here.
        await db.exec(text("""
            SELECT product_key FROM catalog.product
            WHERE product_key IN (
                SELECT variant_product_key FROM catalog.variant WHERE variant_key IN :keys
            ) ORDER BY product_key FOR UPDATE
        """).bindparams(bindparam("keys", expanding=True)), params=params)
        await db.exec(text("""
            SELECT variant_key FROM catalog.variant WHERE variant_key IN :keys
            ORDER BY variant_key FOR UPDATE
        """).bindparams(bindparam("keys", expanding=True)), params=params)
    result = await db.exec(text(_VARIANTS + " WHERE v.variant_key IN :keys ORDER BY v.variant_key")
                           .bindparams(bindparam("keys", expanding=True)), params=params)
    return [dict(row) for row in result.mappings().all()]


async def list_inventory_variants(db: AsyncSession, *, q: str = "", category_key: UUID | None = None,
                                  offset: int = 0, limit: int | None = 20) -> tuple[list[dict], int]:
    conditions, params = [], {"offset": offset, "limit": limit}
    if q.strip():
        conditions.append("lower(p.product_name) LIKE lower(:pattern) ESCAPE '\\'")
        escaped = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        params["pattern"] = f"%{escaped}%"
    if category_key is not None:
        conditions.append("p.product_category_key = :category_key")
        params["category_key"] = category_key
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    count = await db.exec(text("SELECT count(*) FROM catalog.variant v JOIN catalog.product p "
                              "ON p.product_key = v.variant_product_key" + where), params=params)
    total = count.scalar_one()
    result = await db.exec(text(_VARIANTS + where + " ORDER BY p.product_name, v.variant_id LIMIT :limit OFFSET :offset"), params=params)
    return [dict(row) for row in result.mappings().all()], total


async def inventory_categories(db: AsyncSession) -> list[dict]:
    result = await db.exec(text("SELECT category_key, category_name FROM catalog.category ORDER BY category_name, category_key"))
    return [dict(row) for row in result.mappings().all()]
