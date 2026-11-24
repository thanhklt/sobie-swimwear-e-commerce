"""Truy vấn promotion.* qua SQLModel; mọi thao tác nhận session để ghép transaction với ordering.

Tăng / giảm lượt giữ UPDATE nguyên tử (chống race khi đặt / hủy đơn đồng thời).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, text
from sqlmodel import col, select

from app.modules.promotion.models import (
    CodePromotion,
    OrderPromotion,
    ProductPromotion,
    Promotion,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


async def _next_promotion_id(db: AsyncSession) -> str:
    # Serialize code allocation without adding a sequence/table to the schema.
    await db.exec(text("SELECT pg_advisory_xact_lock(64213, 1)"))
    result = await db.exec(text("""
        SELECT COALESCE(MAX(substring(promotion_id FROM 4)::integer), 0) + 1 AS next_no
        FROM promotion.promotion
    """))
    next_no = result.mappings().one()["next_no"]
    if next_no > 9999:
        raise ValueError("Đã hết dải mã khuyến mãi KM-0001 đến KM-9999.")
    return f"KM-{next_no:04d}"


async def create_promotion(db: AsyncSession, data: dict[str, Any]) -> dict[str, Any]:
    promotion_id = await _next_promotion_id(db)
    row = Promotion(
        promotion_id=promotion_id,
        promotion_type=data["promotion_type"],
        promotion_quantity=data.get("quantity"),
        promotion_start_date=data.get("start_date"),
        promotion_end_date=data.get("end_date"),
        promotion_status="ENABLED",
        promotion_used_amount=0,
    )
    db.add(row)
    await db.flush()

    if data["promotion_type"] == "PRODUCT":
        db.add(ProductPromotion(
            promotion_key=row.promotion_key,
            product_promotion_product_key=data["product_key"],
            product_promotion_discount_percentage=data["discount_percentage"],
        ))
    elif data["promotion_type"] == "ORDER":
        db.add(OrderPromotion(
            promotion_key=row.promotion_key,
            order_promotion_discount_percentage=data["discount_percentage"],
            order_promotion_thresh_price=data["threshold_price"],
        ))
    else:
        db.add(CodePromotion(
            promotion_key=row.promotion_key,
            code_promotion_code=data["code"],
            code_promotion_discount_percentage=data["discount_percentage"],
            code_promotion_thresh_price=data["threshold_price"],
        ))
    await db.flush()

    created = {
        "promotion_key": row.promotion_key,
        "promotion_id": promotion_id,
        "promotion_type": row.promotion_type,
        "promotion_status": row.promotion_status,
        "promotion_quantity": row.promotion_quantity,
        "promotion_used_amount": row.promotion_used_amount,
        "promotion_start_date": row.promotion_start_date,
        "promotion_end_date": row.promotion_end_date,
    }
    created.update(data)
    return created


async def list_promotions(db: AsyncSession, promotion_type: str | None = None) -> list[dict[str, Any]]:
    # UNION keep as SQL — three subtype joins stay clearer and match index usage.
    result = await db.exec(text("""
        SELECT p.promotion_id, p.promotion_type, p.promotion_status,
               p.promotion_quantity, p.promotion_used_amount,
               p.promotion_start_date, p.promotion_end_date,
               pp.product_promotion_discount_percentage AS discount_percentage,
               pp.product_promotion_product_key AS product_key, NULL::varchar AS code,
               NULL::numeric AS threshold_price
        FROM promotion.promotion p
        JOIN promotion.product_promotion pp USING (promotion_key)
        WHERE p.promotion_type = 'PRODUCT'
        UNION ALL
        SELECT p.promotion_id, p.promotion_type, p.promotion_status,
               p.promotion_quantity, p.promotion_used_amount,
               p.promotion_start_date, p.promotion_end_date,
               op.order_promotion_discount_percentage, NULL::uuid, NULL::varchar,
               op.order_promotion_thresh_price
        FROM promotion.promotion p
        JOIN promotion.order_promotion op USING (promotion_key)
        UNION ALL
        SELECT p.promotion_id, p.promotion_type, p.promotion_status,
               p.promotion_quantity, p.promotion_used_amount,
               p.promotion_start_date, p.promotion_end_date,
               cp.code_promotion_discount_percentage, NULL::uuid,
               cp.code_promotion_code, cp.code_promotion_thresh_price
        FROM promotion.promotion p
        JOIN promotion.code_promotion cp USING (promotion_key)
        ORDER BY promotion_start_date NULLS FIRST, promotion_id
    """))
    rows = [dict(row) for row in result.mappings().all()]
    return rows if promotion_type is None else [row for row in rows if row["promotion_type"] == promotion_type]


async def product_has_active_promotion(db: AsyncSession, product_key) -> bool:
    statement = (
        select(ProductPromotion.promotion_key)
        .join(Promotion, col(ProductPromotion.promotion_key) == col(Promotion.promotion_key))
        .where(
            ProductPromotion.product_promotion_product_key == product_key,
            Promotion.promotion_status == "ENABLED",
        )
        .limit(1)
    )
    result = await db.exec(statement)
    return result.first() is not None


async def code_promotion_exists(db: AsyncSession, code: str) -> bool:
    statement = (
        select(CodePromotion.promotion_key)
        .where(func.lower(CodePromotion.code_promotion_code) == code.strip().lower())
        .limit(1)
    )
    result = await db.exec(statement)
    return result.first() is not None


async def end_promotion(db: AsyncSession, promotion_id: str) -> bool:
    statement = select(Promotion).where(
        Promotion.promotion_id == promotion_id,
        Promotion.promotion_status == "ENABLED",
    )
    result = await db.exec(statement)
    row = result.one_or_none()
    if row is None:
        return False
    row.promotion_status = "DISABLED"
    db.add(row)
    await db.flush()
    return True


async def product_promotion_for_product(db: AsyncSession, product_key) -> dict[str, Any] | None:
    statement = (
        select(Promotion, ProductPromotion)
        .join(ProductPromotion, col(ProductPromotion.promotion_key) == col(Promotion.promotion_key))
        .where(
            ProductPromotion.product_promotion_product_key == product_key,
            Promotion.promotion_status == "ENABLED",
        )
    )
    result = await db.exec(statement)
    pair = result.first()
    if pair is None:
        return None
    promotion, product = pair
    return {
        "promotion_key": promotion.promotion_key,
        "promotion_id": promotion.promotion_id,
        "discount_percentage": product.product_promotion_discount_percentage,
    }


async def product_promotion_discount(db: AsyncSession, promotion_key) -> Decimal | None:
    statement = select(ProductPromotion).where(ProductPromotion.promotion_key == promotion_key)
    result = await db.exec(statement)
    row = result.one_or_none()
    return Decimal(row.product_promotion_discount_percentage) if row else None


async def find_eligible_order_promotions(db: AsyncSession, subtotal: int, now: Any) -> list[dict[str, Any]]:
    statement = (
        select(Promotion, OrderPromotion)
        .join(OrderPromotion, col(OrderPromotion.promotion_key) == col(Promotion.promotion_key))
        .where(
            Promotion.promotion_status == "ENABLED",
            Promotion.promotion_start_date <= now,
            Promotion.promotion_end_date > now,
            Promotion.promotion_used_amount < Promotion.promotion_quantity,
            OrderPromotion.order_promotion_thresh_price <= subtotal,
        )
    )
    result = await db.exec(statement)
    rows = []
    for promotion, order in result.all():
        rows.append({
            "promotion_key": promotion.promotion_key,
            "promotion_id": promotion.promotion_id,
            "promotion_quantity": promotion.promotion_quantity,
            "promotion_used_amount": promotion.promotion_used_amount,
            "discount_percentage": order.order_promotion_discount_percentage,
            "threshold_price": int(order.order_promotion_thresh_price),
        })
    return rows


async def find_code_promotion(db: AsyncSession, code: str) -> dict[str, Any] | None:
    statement = (
        select(Promotion, CodePromotion)
        .join(CodePromotion, col(CodePromotion.promotion_key) == col(Promotion.promotion_key))
        .where(func.lower(CodePromotion.code_promotion_code) == code.strip().lower())
    )
    result = await db.exec(statement)
    pair = result.first()
    if pair is None:
        return None
    promotion, code_row = pair
    return {
        "promotion_key": promotion.promotion_key,
        "promotion_id": promotion.promotion_id,
        "promotion_status": promotion.promotion_status,
        "promotion_quantity": promotion.promotion_quantity,
        "promotion_used_amount": promotion.promotion_used_amount,
        "promotion_start_date": promotion.promotion_start_date,
        "promotion_end_date": promotion.promotion_end_date,
        "discount_percentage": code_row.code_promotion_discount_percentage,
        "threshold_price": int(code_row.code_promotion_thresh_price),
        "code": code_row.code_promotion_code,
    }


async def increment_used(db: AsyncSession, promotion_key: Any) -> bool:
    """Atomic consume — required for concurrent checkout (UC-31 AC-10)."""
    result = await db.exec(text("""
        UPDATE promotion.promotion
        SET promotion_used_amount = promotion_used_amount + 1
        WHERE promotion_key = :promotion_key AND promotion_status = 'ENABLED'
          AND promotion_used_amount < promotion_quantity
        RETURNING promotion_key
    """), params={"promotion_key": promotion_key})
    return result.first() is not None


async def decrement_used(db: AsyncSession, promotion_key: Any) -> None:
    """Atomic refund — keep used_amount non-negative on cancel."""
    await db.exec(text("""
        UPDATE promotion.promotion
        SET promotion_used_amount = GREATEST(0, promotion_used_amount - 1)
        WHERE promotion_key = :promotion_key
    """), params={"promotion_key": promotion_key})
