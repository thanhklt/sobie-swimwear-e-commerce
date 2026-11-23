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

Không truy vấn bảng của module khác.
"""

from uuid import UUID

from sqlalchemy import Uuid, bindparam, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.catalog.schemas import VariantSummary

_VARIANTS = text(
    """
    SELECT variant.variant_key, variant.variant_id, product.product_id,
           product.product_name, variant.variant_sell_price
    FROM catalog.variant AS variant
    JOIN catalog.product AS product ON product.product_key = variant.variant_product_key
    WHERE variant.variant_key IN :variant_keys
    """
).bindparams(bindparam("variant_keys", expanding=True, type_=Uuid()))


async def get_variants(
    db: AsyncSession, variant_keys: set[UUID]
) -> dict[UUID, VariantSummary]:
    result = await db.exec(_VARIANTS, params={"variant_keys": tuple(variant_keys)})
    return {
        variant_key: VariantSummary(
            sku,
            product_code,
            product_name,
            int(sell_price) if sell_price is not None else None,
        )
        for variant_key, sku, product_code, product_name, sell_price in result
    }
