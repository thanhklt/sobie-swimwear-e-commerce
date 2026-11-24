"""Tầng Repository của module ordering: truy vấn các bảng do module sở hữu:
- ordering.payment
- ordering.order
- ordering.order_detail
- ordering.order_status_history
- ordering.invoice

Không truy vấn bảng của module khác.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering.schemas import SalesStats, VariantSales

_SALES_STATS = (
    text(
        """
        WITH delivered AS (
            SELECT sale.order_key, sale.order_total_price - sale.order_shipping_fee AS revenue
            FROM ordering."order" AS sale
            WHERE sale.order_status = 'DELIVERED'
              AND EXISTS (
                  SELECT 1 FROM ordering.order_status_history AS history
                  WHERE history.order_status_history_order_key = sale.order_key
                    AND history.order_status_history_to_value = 'DELIVERED'
                    AND history.order_status_history_changed_time >= :starts_at
                    AND history.order_status_history_changed_time < :ends_before
              )
        ), sold_variants AS (
            SELECT detail.order_detail_variant_key AS variant_key,
                   SUM(detail.order_detail_quantity) AS quantity,
                   SUM(detail.order_detail_quantity * detail.order_detail_cost_price) AS cost
            FROM delivered
            JOIN ordering.order_detail AS detail ON detail.order_detail_order_key = delivered.order_key
            GROUP BY detail.order_detail_variant_key
        ), created_orders_by_status AS (
            SELECT order_status, COUNT(*) AS quantity
            FROM ordering."order"
            WHERE order_created_date >= :starts_at AND order_created_date < :ends_before
            GROUP BY order_status
        )
        SELECT (SELECT COALESCE(SUM(revenue), 0) FROM delivered) AS revenue,
               COALESCE(SUM(cost), 0) AS cost_of_goods,
               COALESCE(jsonb_object_agg(variant_key::text, quantity), '{}'::jsonb) AS units_by_variant,
               (SELECT COALESCE(jsonb_object_agg(order_status, quantity), '{}'::jsonb)
                FROM created_orders_by_status) AS orders_by_status
        FROM sold_variants
        """
    )
    .bindparams(
        bindparam("starts_at", type_=DateTime(timezone=True)),
        bindparam("ends_before", type_=DateTime(timezone=True)),
    )
    .columns(units_by_variant=JSONB, orders_by_status=JSONB)
)

_UNITS_SOLD = text(
    """
    SELECT detail.order_detail_variant_key,
           SUM(detail.order_detail_quantity),
           MAX(sale.order_created_date)
    FROM ordering."order" AS sale
    JOIN ordering.order_detail AS detail ON detail.order_detail_order_key = sale.order_key
    WHERE sale.order_created_date >= :starts_at
      AND sale.order_created_date <= :ends_at
      AND sale.order_status IN ('PENDING', 'CONFIRMED', 'AWAITING_PICKUP', 'SHIPPING', 'DELIVERED')
    GROUP BY detail.order_detail_variant_key
    """
).bindparams(
    bindparam("starts_at", type_=DateTime(timezone=True)),
    bindparam("ends_at", type_=DateTime(timezone=True)),
)


async def get_sales_stats(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> SalesStats:
    result = await db.exec(
        _SALES_STATS, params={"starts_at": starts_at, "ends_before": ends_before}
    )
    row = result.mappings().one()
    return SalesStats(
        revenue=int(row["revenue"]),
        cost_of_goods=int(row["cost_of_goods"]),
        units_by_variant={
            UUID(variant_key): quantity
            for variant_key, quantity in row["units_by_variant"].items()
        },
        orders_by_status=row["orders_by_status"],
    )


async def get_units_sold(
    db: AsyncSession, starts_at: datetime, ends_at: datetime
) -> dict[UUID, VariantSales]:
    result = await db.exec(
        _UNITS_SOLD, params={"starts_at": starts_at, "ends_at": ends_at}
    )
    return {
        variant_key: VariantSales(quantity, latest_order_at)
        for variant_key, quantity, latest_order_at in result
    }
