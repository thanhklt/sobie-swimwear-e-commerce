"""Tác vụ định kỳ ordering — UC-24 tự hủy đơn QR quá hạn."""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.ordering import adapters, service
from app.modules.ordering.dependencies import NoPromotionGateway
from app.shared.database.engine import session_factory


async def run_auto_cancel_overdue_qr(*, now: datetime | None = None) -> list[str]:
    """Chạy một vòng UC-24. Caller (scheduler) gọi mỗi 5 phút [GD]."""
    current = now or datetime.now(UTC)
    async with session_factory() as db:
        return await service.auto_cancel_overdue_qr_orders(
            db,
            inventory=adapters.DbInventoryGateway(db),
            promotion=NoPromotionGateway(),
            now=current,
        )
