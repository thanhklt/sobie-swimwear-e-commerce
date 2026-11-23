"""Truy vấn thuộc schema catalog."""

from sqlalchemy import bindparam, text


_INVOICE_VARIANTS = text('''
    SELECT v.variant_key, v.variant_id, p.product_name, c.color_name, s.size_name
    FROM catalog.variant v
    JOIN catalog.product p ON p.product_key = v.variant_product_key
    JOIN catalog.color c ON c.color_key = v.variant_color_key
    JOIN catalog.size s ON s.size_key = v.variant_size_key
    WHERE v.variant_key IN :variant_keys
''').bindparams(bindparam("variant_keys", expanding=True))


async def invoice_variant_details(db, variant_keys):
    if not variant_keys:
        return {}
    result = await db.exec(_INVOICE_VARIANTS, params={"variant_keys": variant_keys})
    return {row["variant_key"]: dict(row) for row in result.mappings().all()}


async def active_product_key(db, product_id: str):
    result = await db.exec(text("""
        SELECT product_key FROM catalog.product
        WHERE product_id = :product_id AND product_status = 'ACTIVE'
    """), params={"product_id": product_id})
    row = result.first()
    return row[0] if row else None


async def product_ids_by_keys(db, product_keys):
    if not product_keys:
        return {}
    stmt = text("SELECT product_key, product_id FROM catalog.product WHERE product_key IN :keys").bindparams(
        bindparam("keys", expanding=True)
    )
    result = await db.exec(stmt, params={"keys": product_keys})
    return {row["product_key"]: row["product_id"] for row in result.mappings().all()}
