"""Tầng Service của module inventory: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Đọc tồn kho theo biến thể (cho catalog, shopping, reporting).
- Trừ / cộng tồn trong transaction của bên gọi (cho ordering).
- Đọc giá vốn hiện tại (cho ordering, reporting).
- Tạo dòng tồn kho khi tạo biến thể (cho catalog).
- Đọc tồn kho thấp và tiền nhập theo nhà cung cấp (cho reporting).

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from datetime import datetime
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.inventory import repository
from app.modules.inventory.schemas import PurchaseTotal

LOW_STOCK_THRESHOLD = 5


# UC-37 Xem dashboard — Main Flow 3.5, AC-4 và AC-6
# specs/use-cases/reporting/UC-37-view-dashboard.md
async def get_stock(db: AsyncSession) -> dict[UUID, int]:
    return await repository.get_stock(db, LOW_STOCK_THRESHOLD)


async def get_purchase_totals(
    db: AsyncSession, starts_at: datetime, ends_before: datetime
) -> list[PurchaseTotal]:
    return await repository.get_purchase_totals(db, starts_at, ends_before)
