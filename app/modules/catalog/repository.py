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

Không truy vấn bảng của module khác. Chưa triển khai.
"""

from sqlalchemy import text


async def find_cart_variants(db, variant_keys):
    rows = await db.execute(text("""
        SELECT v.variant_key, v.variant_id, p.product_name,
               (v.variant_status = 'ACTIVE' AND p.product_status = 'ACTIVE'
                AND v.variant_sell_price IS NOT NULL) AS sellable
        FROM catalog.variant v
        JOIN catalog.product p ON p.product_key = v.variant_product_key
        WHERE v.variant_key = ANY(:variant_keys)
    """), {"variant_keys": list(variant_keys)})
    return {row.variant_key: row for row in rows}
