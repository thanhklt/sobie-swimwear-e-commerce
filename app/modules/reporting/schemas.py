"""Dữ liệu kỳ báo cáo và các chỉ số hiển thị trên dashboard."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.modules.inventory.schemas import PurchaseTotal

REPORTING_TIME_ZONE = ZoneInfo("Asia/Ho_Chi_Minh")


@dataclass(frozen=True, slots=True)
class ReportPeriod:
    start_date: date
    end_date: date

    @classmethod
    def current_month(cls) -> "ReportPeriod":
        today = datetime.now(REPORTING_TIME_ZONE).date()
        final_day = monthrange(today.year, today.month)[1]
        return cls(today.replace(day=1), today.replace(day=final_day))

    def utc_bounds(self) -> tuple[datetime, datetime]:
        start = datetime.combine(self.start_date, time.min, REPORTING_TIME_ZONE)
        end = datetime.combine(
            self.end_date + timedelta(days=1), time.min, REPORTING_TIME_ZONE
        )
        return start.astimezone(UTC), end.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class TopProduct:
    code: str
    name: str
    quantity: int


@dataclass(frozen=True, slots=True)
class LowStock:
    sku: str
    product_name: str
    quantity: int


@dataclass(frozen=True, slots=True)
class Dashboard:
    revenue: int
    gross_profit: int
    orders_by_status: dict[str, int]
    top_products: list[TopProduct]
    low_stock: list[LowStock]
    purchase_totals: list[PurchaseTotal]
