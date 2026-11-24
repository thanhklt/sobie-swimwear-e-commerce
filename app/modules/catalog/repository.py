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

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.catalog.models import Product, ProductVariant
from app.modules.catalog.schemas import VariantSummary


async def get_variants(
    db: AsyncSession, variant_keys: set[UUID]
) -> dict[UUID, VariantSummary]:
    statement = (
        select(
            ProductVariant.variant_key,
            ProductVariant.variant_id,
            Product.product_id,
            Product.product_name,
            ProductVariant.variant_sell_price,
        )
        .select_from(ProductVariant)
        .join(Product, ProductVariant.variant_product_key == Product.product_key)
        .where(ProductVariant.variant_key.in_(tuple(variant_keys)))
    )
    result = await db.exec(statement)
    return {
        variant_key: VariantSummary(
            sku,
            product_code,
            product_name,
            int(sell_price) if sell_price is not None else None,
        )
        for variant_key, sku, product_code, product_name, sell_price in result
    }
