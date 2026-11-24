"""Tầng Repository của module inventory: truy vấn các bảng do module sở hữu:
- inventory.supplier
- inventory.goods_receipt
- inventory.goods_receipt_detail
- inventory.stock

Không truy vấn bảng của module khác.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.inventory.models import GoodsReceipt, Stock, Supplier
from app.modules.inventory.schemas import PurchaseTotal


async def get_stock(db: AsyncSession, threshold: int) -> dict[UUID, int]:
    statement = select(Stock.stock_variant_key, Stock.stock_quantity).where(
        Stock.stock_quantity <= threshold
    )
    result = await db.exec(statement)
    return {variant_key: quantity for variant_key, quantity in result}


async def get_purchase_totals(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> list[PurchaseTotal]:
    statement = (
        select(
            Supplier.supplier_id,
            Supplier.supplier_name,
            func.sum(GoodsReceipt.goods_receipt_final_price),
        )
        .select_from(GoodsReceipt)
        .join(
            Supplier, GoodsReceipt.goods_receipt_supplier_key == Supplier.supplier_key
        )
        .where(
            GoodsReceipt.goods_receipt_status == "CONFIRMED",
            GoodsReceipt.goods_receipt_created_date >= starts_at,
            GoodsReceipt.goods_receipt_created_date < ends_before,
        )
        .group_by(Supplier.supplier_key)
        .order_by(Supplier.supplier_id)
    )
    result = await db.exec(statement)
    return [PurchaseTotal(code, name, int(amount)) for code, name, amount in result]
