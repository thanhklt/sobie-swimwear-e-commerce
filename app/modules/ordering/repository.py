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

from sqlalchemy import String, cast, func, literal
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering.models import Order, OrderDetail, OrderStatusHistory
from app.modules.ordering.schemas import SalesStats, VariantSales

_BESTSELLER_ORDER_STATUSES = (
    "PENDING",
    "CONFIRMED",
    "AWAITING_PICKUP",
    "SHIPPING",
    "DELIVERED",
)


async def get_sales_stats(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> SalesStats:
    delivered_in_period = (
        select(OrderStatusHistory.order_status_history_key)
        .where(
            OrderStatusHistory.order_status_history_order_key == Order.order_key,
            OrderStatusHistory.order_status_history_to_value == "DELIVERED",
            OrderStatusHistory.order_status_history_changed_time >= starts_at,
            OrderStatusHistory.order_status_history_changed_time < ends_before,
        )
        .correlate(Order)
        .exists()
    )
    delivered = (
        select(
            Order.order_key,
            (Order.order_total_price - Order.order_shipping_fee).label("revenue"),
        )
        .where(Order.order_status == "DELIVERED", delivered_in_period)
        .cte("delivered")
    )
    sold_variants = (
        select(
            OrderDetail.order_detail_variant_key.label("variant_key"),
            func.sum(OrderDetail.order_detail_quantity).label("quantity"),
            func.sum(
                OrderDetail.order_detail_quantity * OrderDetail.order_detail_cost_price
            ).label("cost"),
        )
        .select_from(OrderDetail)
        .join(delivered, OrderDetail.order_detail_order_key == delivered.c.order_key)
        .group_by(OrderDetail.order_detail_variant_key)
        .cte("sold_variants")
    )
    created_orders = (
        select(Order.order_status, func.count().label("quantity"))
        .where(
            Order.order_created_date >= starts_at,
            Order.order_created_date < ends_before,
        )
        .group_by(Order.order_status)
        .cte("created_orders_by_status")
    )

    # Tổng doanh thu trên tập đơn để mỗi đơn được cộng đúng một lần.
    revenue = select(func.coalesce(func.sum(delivered.c.revenue), 0)).scalar_subquery()
    empty_object = literal({}, type_=JSONB())
    units_by_variant = func.coalesce(
        func.jsonb_object_agg(
            cast(sold_variants.c.variant_key, String()),
            sold_variants.c.quantity,
            type_=JSONB(),
        ),
        empty_object,
    )
    orders_by_status = select(
        func.coalesce(
            func.jsonb_object_agg(
                created_orders.c.order_status, created_orders.c.quantity, type_=JSONB()
            ),
            empty_object,
        )
    ).scalar_subquery()
    statement = select(
        revenue.label("revenue"),
        func.coalesce(func.sum(sold_variants.c.cost), 0).label("cost_of_goods"),
        units_by_variant.label("units_by_variant"),
        orders_by_status.label("orders_by_status"),
    ).select_from(sold_variants)
    result = await db.exec(statement)
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
    statement = (
        select(
            OrderDetail.order_detail_variant_key,
            func.sum(OrderDetail.order_detail_quantity),
            func.max(Order.order_created_date),
        )
        .select_from(Order)
        .join(OrderDetail, OrderDetail.order_detail_order_key == Order.order_key)
        .where(
            Order.order_created_date >= starts_at,
            Order.order_created_date <= ends_at,
            Order.order_status.in_(_BESTSELLER_ORDER_STATUSES),
        )
        .group_by(OrderDetail.order_detail_variant_key)
    )
    result = await db.exec(statement)
    return {
        variant_key: VariantSales(quantity, latest_order_at)
        for variant_key, quantity, latest_order_at in result
    }
