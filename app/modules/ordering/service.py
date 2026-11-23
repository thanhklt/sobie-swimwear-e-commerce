"""Tầng Service của module ordering: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Đổi trạng thái đơn khi bàn giao / vận chuyển (cho shipping).
- Tìm đơn QR theo order_code và đánh dấu Đã thanh toán (cho payment).
- Đọc số liệu bán hàng và số đơn theo trạng thái qua get_sales_stats() (cho reporting).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ordering import repository
from app.modules.ordering.schemas import SalesStats


# UC-37 Xem dashboard — Main Flow 3.1–3.4, AC-1–AC-3 và AC-9
# specs/use-cases/reporting/UC-37-view-dashboard.md
async def get_sales_stats(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> SalesStats:
    return await repository.get_sales_stats(db, starts_at, ends_before)
