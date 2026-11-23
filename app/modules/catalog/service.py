"""Tầng Service của module catalog: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Lấy thông tin biến thể và giá bán hiện tại (cho shopping, ordering, reporting).
- Kiểm tra sản phẩm / biến thể đang bán.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.catalog import repository
from app.modules.catalog.schemas import VariantSummary


# UC-18–UC-20 — Tra thông tin biến thể và giá bán hiện tại cho giỏ hàng và đặt hàng.
# UC-37 Xem dashboard — AC-3, AC-4 và AC-6 (specs/use-cases/reporting/UC-37-view-dashboard.md)
async def get_variants(
    db: AsyncSession, variant_keys: set[UUID]
) -> dict[UUID, VariantSummary]:
    """Tra cứu theo ID, bao gồm biến thể đã ngừng bán."""
    if not variant_keys:
        return {}
    return await repository.get_variants(db, variant_keys)
