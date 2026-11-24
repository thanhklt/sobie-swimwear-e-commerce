"""Truy vấn promotion.*; mọi thao tác nhận session để ghép transaction với ordering."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import text

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
    result = await db.exec(text("""
        INSERT INTO promotion.promotion
            (promotion_id, promotion_type, promotion_quantity,
             promotion_start_date, promotion_end_date)
        VALUES (:promotion_id, :promotion_type, :quantity, :start_date, :end_date)
        RETURNING promotion_key, promotion_id, promotion_type, promotion_status,
                  promotion_quantity, promotion_used_amount,
                  promotion_start_date, promotion_end_date
    """), params={**data, "promotion_id": promotion_id})
    row = dict(result.mappings().one())
    row["promotion_id"] = promotion_id
    if data["promotion_type"] == "PRODUCT":
        await db.exec(text("""
            INSERT INTO promotion.product_promotion
                (promotion_key, product_promotion_product_key,
                 product_promotion_discount_percentage)
            VALUES (:promotion_key, :product_key, :discount_percentage)
        """), params={**data, "promotion_key": row["promotion_key"]})
    elif data["promotion_type"] == "ORDER":
        await db.exec(text("""
            INSERT INTO promotion.order_promotion
                (promotion_key, order_promotion_discount_percentage, order_promotion_thresh_price)
            VALUES (:promotion_key, :discount_percentage, :threshold_price)
        """), params={**data, "promotion_key": row["promotion_key"]})
    else:
        await db.exec(text("""
            INSERT INTO promotion.code_promotion
                (promotion_key, code_promotion_code, code_promotion_discount_percentage,
                 code_promotion_thresh_price)
            VALUES (:promotion_key, :code, :discount_percentage, :threshold_price)
        """), params={**data, "promotion_key": row["promotion_key"]})
    row.update(data)
    return row


async def list_promotions(db: AsyncSession, promotion_type: str | None = None) -> list[dict[str, Any]]:
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
    """), params={"promotion_type": promotion_type})
    rows = [dict(row) for row in result.mappings().all()]
    return rows if promotion_type is None else [row for row in rows if row["promotion_type"] == promotion_type]


async def product_has_active_promotion(db: AsyncSession, product_key) -> bool:
    result = await db.exec(text("""
        SELECT 1
        FROM promotion.product_promotion pp
        JOIN promotion.promotion p USING (promotion_key)
        WHERE pp.product_promotion_product_key = :product_key AND p.promotion_status = 'ENABLED'
        LIMIT 1
    """), params={"product_key": product_key})
    return result.first() is not None


async def end_promotion(db: AsyncSession, promotion_id: str) -> bool:
    result = await db.exec(text("""
        UPDATE promotion.promotion
        SET promotion_status = 'DISABLED'
        WHERE promotion_id = :promotion_id AND promotion_status = 'ENABLED'
        RETURNING promotion_key
    """), params={"promotion_id": promotion_id})
    return result.first() is not None


async def product_promotion_for_product(db: AsyncSession, product_key) -> dict[str, Any] | None:
    result = await db.exec(text("""
        SELECT p.promotion_key, p.promotion_id,
               pp.product_promotion_discount_percentage AS discount_percentage
        FROM promotion.product_promotion pp
        JOIN promotion.promotion p USING (promotion_key)
        WHERE pp.product_promotion_product_key = :product_key AND p.promotion_status = 'ENABLED'
    """), params={"product_key": product_key})
    row = result.mappings().one_or_none()
    return dict(row) if row else None


async def product_promotion_discount(db: AsyncSession, promotion_key) -> Decimal | None:
    result = await db.exec(text("""
        SELECT product_promotion_discount_percentage
        FROM promotion.product_promotion WHERE promotion_key = :promotion_key
    """), params={"promotion_key": promotion_key})
    row = result.first()
    return Decimal(row[0]) if row else None


async def find_eligible_order_promotions(db: AsyncSession, subtotal: int, now: Any) -> list[dict[str, Any]]:
    result = await db.exec(text("""
        SELECT p.promotion_key, p.promotion_id, p.promotion_quantity, p.promotion_used_amount,
               op.order_promotion_discount_percentage AS discount_percentage,
               op.order_promotion_thresh_price AS threshold_price
        FROM promotion.promotion p
        JOIN promotion.order_promotion op USING (promotion_key)
        WHERE p.promotion_status = 'ENABLED'
          AND p.promotion_start_date <= :now AND p.promotion_end_date > :now
          AND p.promotion_used_amount < p.promotion_quantity
          AND op.order_promotion_thresh_price <= :subtotal
    """), params={"subtotal": subtotal, "now": now})
    return [dict(row) for row in result.mappings().all()]


async def find_code_promotion(db: AsyncSession, code: str) -> dict[str, Any] | None:
    result = await db.exec(text("""
        SELECT p.promotion_key, p.promotion_id, p.promotion_status,
               p.promotion_quantity, p.promotion_used_amount,
               p.promotion_start_date, p.promotion_end_date,
               cp.code_promotion_discount_percentage AS discount_percentage,
               cp.code_promotion_thresh_price AS threshold_price,
               cp.code_promotion_code AS code
        FROM promotion.code_promotion cp
        JOIN promotion.promotion p USING (promotion_key)
        WHERE lower(cp.code_promotion_code) = lower(:code)
    """), params={"code": code.strip()})
    row = result.mappings().one_or_none()
    return dict(row) if row else None


async def increment_used(db: AsyncSession, promotion_key: Any) -> bool:
    result = await db.exec(text("""
        UPDATE promotion.promotion
        SET promotion_used_amount = promotion_used_amount + 1
        WHERE promotion_key = :promotion_key AND promotion_status = 'ENABLED'
          AND promotion_used_amount < promotion_quantity
        RETURNING promotion_key
    """), params={"promotion_key": promotion_key})
    return result.first() is not None


async def decrement_used(db: AsyncSession, promotion_key: Any) -> None:
    await db.exec(text("""
        UPDATE promotion.promotion
        SET promotion_used_amount = GREATEST(0, promotion_used_amount - 1)
        WHERE promotion_key = :promotion_key
    """), params={"promotion_key": promotion_key})
