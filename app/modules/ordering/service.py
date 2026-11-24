"""Tầng Service của module ordering: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Đổi trạng thái đơn khi bàn giao / vận chuyển (cho shipping).
- Tìm đơn QR theo order_code và đánh dấu Đã thanh toán (cho payment).
- Đọc số liệu bán hàng và số đơn theo trạng thái qua get_sales_stats() (cho reporting).
- Đọc số lượng theo biến thể và thời điểm đặt gần nhất qua get_units_sold() (cho reporting).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from datetime import datetime
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import repository
from app.modules.ordering.schemas import SalesStats, VariantSales


# UC-37 Xem dashboard — Main Flow 3.1–3.4, AC-1–AC-3 và AC-9
# specs/use-cases/reporting/UC-37-view-dashboard.md
async def get_sales_stats(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> SalesStats:
    return await repository.get_sales_stats(db, starts_at, ends_before)


# UC-09 Xem trang chủ — AC-8, AC-9, AC-12 và AC-13
# specs/use-cases/catalog/UC-09-view-home-page.md
async def get_units_sold(
    db: AsyncSession, starts_at: datetime, ends_at: datetime
) -> dict[UUID, VariantSales]:
    return await repository.get_units_sold(db, starts_at, ends_at)
