"""Tầng Repository của module inventory: truy vấn các bảng do module sở hữu:
- inventory.supplier
- inventory.goods_receipt
- inventory.goods_receipt_detail
- inventory.stock

Không truy vấn bảng của module khác. Chưa triển khai.
"""

from sqlalchemy import text


async def lock_stock_quantities(db, variant_keys):
    rows = await db.execute(text("""
        SELECT stock_variant_key, stock_quantity
        FROM inventory.stock WHERE stock_variant_key = ANY(:variant_keys)
        ORDER BY stock_variant_key FOR SHARE
    """), {"variant_keys": list(variant_keys)})
    return {row.stock_variant_key: row.stock_quantity for row in rows}
