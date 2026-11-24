"""Kiểu dữ liệu công khai của module ordering, tách biệt với model lưu trữ."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SalesStats:
    revenue: int
    cost_of_goods: int
    units_by_variant: dict[UUID, int]
    orders_by_status: dict[str, int]


@dataclass(frozen=True, slots=True)
class VariantSales:
    quantity: int
    latest_order_at: datetime
