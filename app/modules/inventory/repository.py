"""Tầng Repository của module inventory: truy vấn các bảng do module sở hữu:
- inventory.supplier
- inventory.goods_receipt
- inventory.goods_receipt_detail
- inventory.stock

Không truy vấn bảng của module khác.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, bindparam, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.inventory.schemas import PurchaseTotal

_LOW_STOCK = text(
    """
    SELECT stock_variant_key, stock_quantity
    FROM inventory.stock
    WHERE stock_quantity <= :threshold
    """
)

_PURCHASE_TOTALS = text(
    """
    SELECT supplier.supplier_id, supplier.supplier_name, SUM(receipt.goods_receipt_final_price)
    FROM inventory.goods_receipt AS receipt
    JOIN inventory.supplier AS supplier ON supplier.supplier_key = receipt.goods_receipt_supplier_key
    WHERE receipt.goods_receipt_status = 'CONFIRMED'
      AND receipt.goods_receipt_created_date >= :starts_at
      AND receipt.goods_receipt_created_date < :ends_before
    GROUP BY supplier.supplier_key
    ORDER BY supplier.supplier_id
    """
).bindparams(
    bindparam("starts_at", type_=DateTime(timezone=True)),
    bindparam("ends_before", type_=DateTime(timezone=True)),
)


async def get_stock(db: AsyncSession, threshold: int) -> dict[UUID, int]:
    result = await db.exec(_LOW_STOCK, params={"threshold": threshold})
    return {variant_key: quantity for variant_key, quantity in result}


async def get_purchase_totals(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> list[PurchaseTotal]:
    result = await db.exec(
        _PURCHASE_TOTALS, params={"starts_at": starts_at, "ends_before": ends_before}
    )
    return [PurchaseTotal(code, name, int(amount)) for code, name, amount in result]
