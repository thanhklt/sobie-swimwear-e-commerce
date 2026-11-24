"""Adapter tạm [GD] cho UI thử shopping — đọc seed catalog/inventory/identity.

SQLModel ORM map bảng module khác (chỉ cột cần). Thay bằng service công khai
khi teammate sẵn sàng. Shopping service vẫn chỉ nhận protocol.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import col, select

from app.modules.shopping.dependencies import ProductCardData
from app.shared.seed_refs import (
    AccountRef,
    ColorRef,
    GalleryRef,
    ProductRef,
    SizeRef,
    StockRef,
    VariantRef,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

DEMO_EMAIL = "khachhang@example.com"


async def get_account_key_by_email(db: AsyncSession, email: str) -> UUID:
    result = await db.exec(
        select(AccountRef).where(AccountRef.account_email == email)
    )
    account = result.first()
    if account is None:
        raise RuntimeError(f"Không tìm thấy account {email}")
    return account.account_key


async def get_demo_account_key(db: AsyncSession) -> UUID:
    return await get_account_key_by_email(db, DEMO_EMAIL)


async def get_variant_key_by_id(db: AsyncSession, variant_id: str) -> UUID:
    result = await db.exec(
        select(VariantRef).where(VariantRef.variant_id == variant_id)
    )
    variant = result.first()
    if variant is None:
        raise RuntimeError(f"Không tìm thấy variant {variant_id}")
    return variant.variant_key


async def get_product_key_by_id(db: AsyncSession, product_id: str) -> UUID:
    result = await db.exec(
        select(ProductRef).where(ProductRef.product_id == product_id)
    )
    product = result.first()
    if product is None:
        raise RuntimeError(f"Không tìm thấy product {product_id}")
    return product.product_key


async def set_stock_quantity(
    db: AsyncSession, variant_key: UUID, quantity: int
) -> None:
    result = await db.exec(
        select(StockRef)
        .where(StockRef.stock_variant_key == variant_key)
        .with_for_update()
    )
    stock = result.first()
    if stock is None:
        raise RuntimeError(f"Không có dòng stock cho {variant_key}")
    stock.stock_quantity = quantity
    db.add(stock)
    await db.flush()


async def get_stock_quantity(db: AsyncSession, variant_key: UUID) -> int:
    result = await db.exec(
        select(StockRef).where(StockRef.stock_variant_key == variant_key)
    )
    stock = result.first()
    return int(stock.stock_quantity) if stock else 0


async def _first_gallery_url(db: AsyncSession, product_key: UUID) -> str | None:
    result = await db.exec(
        select(GalleryRef)
        .where(GalleryRef.gallery_product_key == product_key)
        .order_by(col(GalleryRef.gallery_order_no))
        .limit(1)
    )
    gallery = result.first()
    return gallery.gallery_url if gallery else None


async def _min_variant_price(db: AsyncSession, product_key: UUID) -> Decimal:
    result = await db.exec(
        select(VariantRef.variant_sell_price).where(
            VariantRef.variant_product_key == product_key
        )
    )
    prices = [Decimal(p) for p in result.all() if p is not None]
    return min(prices) if prices else Decimal("0")


async def list_seed_variants(db: AsyncSession) -> list[dict]:
    result = await db.exec(
        select(
            VariantRef,
            ProductRef.product_name,
            ProductRef.product_status,
            ColorRef.color_name,
            SizeRef.size_name,
            StockRef.stock_quantity,
        )
        .select_from(VariantRef)
        .join(
            ProductRef,
            col(ProductRef.product_key) == col(VariantRef.variant_product_key),
        )
        .join(
            ColorRef,
            col(ColorRef.color_key) == col(VariantRef.variant_color_key),
        )
        .join(
            SizeRef,
            col(SizeRef.size_key) == col(VariantRef.variant_size_key),
        )
        .outerjoin(
            StockRef,
            col(StockRef.stock_variant_key) == col(VariantRef.variant_key),
        )
        .order_by(col(VariantRef.variant_id))
    )
    rows = result.all()
    out: list[dict] = []
    for variant, product_name, product_status, color_name, size_name, stock_qty in rows:
        out.append(
            {
                "variant_key": variant.variant_key,
                "variant_id": variant.variant_id,
                "label": f"{product_name} — {color_name} / {size_name}",
                "price": Decimal(variant.variant_sell_price or 0),
                "stock": int(stock_qty or 0),
                "sellable": product_status == "ACTIVE",
            }
        )
    return out


async def list_seed_products(db: AsyncSession) -> list[dict]:
    result = await db.exec(select(ProductRef).order_by(col(ProductRef.product_id)))
    products = result.all()
    out: list[dict] = []
    for product in products:
        # Chỉ liệt kê sản phẩm có ít nhất 1 variant (giống query cũ JOIN variant)
        has_variant = (
            await db.exec(
                select(VariantRef.variant_key)
                .where(VariantRef.variant_product_key == product.product_key)
                .limit(1)
            )
        ).first()
        if has_variant is None:
            continue
        out.append(
            {
                "product_key": product.product_key,
                "product_id": product.product_id,
                "name": product.product_name,
                "image_url": await _first_gallery_url(db, product.product_key),
                "min_price": await _min_variant_price(db, product.product_key),
                "is_active": product.product_status == "ACTIVE",
            }
        )
    return out


class SeedAvailability:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_stock_quantity(self, variant_key: UUID) -> int:
        return await get_stock_quantity(self._db, variant_key)

    async def is_variant_sellable(self, variant_key: UUID) -> bool:
        result = await self._db.exec(
            select(ProductRef.product_status)
            .select_from(VariantRef)
            .join(
                ProductRef,
                col(ProductRef.product_key) == col(VariantRef.variant_product_key),
            )
            .where(VariantRef.variant_key == variant_key)
        )
        status = result.first()
        return status == "ACTIVE"


class SeedPricing:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_current_unit_price(self, variant_key: UUID) -> Decimal:
        result = await self._db.exec(
            select(VariantRef).where(VariantRef.variant_key == variant_key)
        )
        variant = result.one()
        return Decimal(variant.variant_sell_price or 0)


class SeedProductCatalog:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def product_exists(self, product_key: UUID) -> bool:
        result = await self._db.exec(
            select(ProductRef.product_key).where(ProductRef.product_key == product_key)
        )
        return result.first() is not None

    async def is_product_active(self, product_key: UUID) -> bool:
        result = await self._db.exec(
            select(ProductRef).where(ProductRef.product_key == product_key)
        )
        product = result.first()
        return bool(product and product.product_status == "ACTIVE")

    async def get_product_card(self, product_key: UUID) -> ProductCardData:
        result = await self._db.exec(
            select(ProductRef).where(ProductRef.product_key == product_key)
        )
        product = result.one()
        return ProductCardData(
            product_key=product.product_key,
            product_id=product.product_id,
            name=product.product_name,
            image_url=await _first_gallery_url(self._db, product_key),
            min_price=await _min_variant_price(self._db, product_key),
            is_active=product.product_status == "ACTIVE",
        )


async def variant_labels(db: AsyncSession, variant_keys: list[UUID]) -> dict[UUID, str]:
    if not variant_keys:
        return {}
    all_variants = await list_seed_variants(db)
    wanted = set(variant_keys)
    return {
        v["variant_key"]: v["label"]
        for v in all_variants
        if v["variant_key"] in wanted
    }
