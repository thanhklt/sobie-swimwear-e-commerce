"""Repository ordering — SQLModel ORM, chỉ schema ordering.

Mỗi hàm gắn comment UC phía trên (UC-19 → UC-27 / UC-24 / UC-25).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import func
from sqlmodel import col, select

from app.modules.ordering.models import (
    Invoice,
    Order,
    OrderDetail,
    OrderStatusHistory,
    Payment,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


# UC-19 / UC-20 — resolve payment_key theo tên (COD / QR).
async def get_payment_key(db: AsyncSession, payment_name: str) -> UUID:
    result = await db.exec(
        select(Payment.payment_key).where(Payment.payment_name == payment_name)
    )
    key = result.first()
    if key is None:
        raise RuntimeError(f"Chưa seed phương thức thanh toán {payment_name}")
    return key


# UC-19 / UC-20 / UC-21 — đọc tên phương thức thanh toán từ payment_key.
async def payment_name_of(db: AsyncSession, payment_key: UUID) -> str:
    result = await db.exec(
        select(Payment.payment_name).where(Payment.payment_key == payment_key)
    )
    return str(result.one())


# UC-20 AC-3 — kiểm tra trùng mã đơn trước khi sinh lại.
async def order_code_exists(db: AsyncSession, order_code: str) -> bool:
    result = await db.exec(
        select(Order.order_key).where(Order.order_code == order_code)
    )
    return result.first() is not None


# UC-19 / UC-20 — tạo đơn (snapshot nhận hàng, tổng tiền, trạng thái ban đầu).
async def create_order(db: AsyncSession, order: Order) -> Order:
    db.add(order)
    await db.flush()
    return order


# UC-19 / UC-20 — lưu dòng chi tiết đơn (giá, SL, KM theo SP).
async def add_order_detail(db: AsyncSession, detail: OrderDetail) -> None:
    db.add(detail)
    await db.flush()


# UC-19 / UC-20 (tạo đơn) + UC-21 / UC-22 / UC-23 / UC-24 — ghi lịch sử đổi trạng thái.
async def add_status_history(
    db: AsyncSession,
    *,
    order_key: UUID,
    from_value: str | None,
    to_value: str,
    source: str,
    changed_by: UUID | None = None,
    note: str | None = None,
) -> None:
    db.add(
        OrderStatusHistory(
            order_status_history_order_key=order_key,
            order_status_history_from_value=from_value,
            order_status_history_to_value=to_value,
            order_status_history_source=source,
            order_status_history_changed_by_key=changed_by,
            order_status_history_note=note,
        )
    )
    await db.flush()


# UC-21 / UC-22 / UC-23 / UC-26 — lấy đơn theo khóa nội bộ.
async def get_order_by_key(db: AsyncSession, order_key: UUID) -> Order | None:
    result = await db.exec(select(Order).where(Order.order_key == order_key))
    return result.first()


# UC-21 / UC-22 / UC-23 / UC-20 (xem lại QR) — lấy đơn theo order_code.
async def get_order_by_code(db: AsyncSession, order_code: str) -> Order | None:
    result = await db.exec(select(Order).where(Order.order_code == order_code))
    return result.first()


# UC-21 — danh sách đơn của khách (phân trang).
async def list_orders_for_account(
    db: AsyncSession,
    account_key: UUID,
    *,
    limit: int,
    offset: int,
) -> list[Order]:
    result = await db.exec(
        select(Order)
        .where(Order.order_account_key == account_key)
        .order_by(col(Order.order_created_date).desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.all())


# UC-21 — đếm tổng đơn của khách (phân trang).
async def count_orders_for_account(db: AsyncSession, account_key: UUID) -> int:
    result = await db.exec(
        select(func.count()).select_from(Order).where(Order.order_account_key == account_key)
    )
    return int(result.one())


# UC-23+ (NV) — danh sách đơn theo bộ lọc trạng thái (portal).
async def list_orders_admin(
    db: AsyncSession,
    *,
    status: str | None,
    limit: int,
    offset: int,
) -> list[Order]:
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.order_status == status)
    stmt = stmt.order_by(col(Order.order_created_date).desc()).offset(offset).limit(limit)
    result = await db.exec(stmt)
    return list(result.all())


# UC-21 / UC-26 / UC-27 — dòng chi tiết đơn.
async def list_order_details(db: AsyncSession, order_key: UUID) -> list[OrderDetail]:
    result = await db.exec(
        select(OrderDetail).where(OrderDetail.order_detail_order_key == order_key)
    )
    return list(result.all())


# UC-21 — timeline lịch sử trạng thái đơn.
async def list_status_history(
    db: AsyncSession, order_key: UUID
) -> list[OrderStatusHistory]:
    result = await db.exec(
        select(OrderStatusHistory)
        .where(OrderStatusHistory.order_status_history_order_key == order_key)
        .order_by(
            col(OrderStatusHistory.order_status_history_changed_time),
            col(OrderStatusHistory.order_status_history_key),
        )
    )
    return list(result.all())


# UC-22 / UC-23 / UC-24 / UC-25 (mark paid) — cập nhật order sau đổi trạng thái / thanh toán.
async def save_order(db: AsyncSession, order: Order) -> None:
    from datetime import UTC

    order.order_updated_date = datetime.now(UTC)
    db.add(order)
    await db.flush()


# UC-24 — đơn QR quá hạn chưa thanh toán cần tự hủy.
async def list_overdue_unpaid_qr_orders(
    db: AsyncSession, *, older_than: datetime
) -> list[Order]:
    qr_key = await get_payment_key(db, "QR")
    result = await db.exec(
        select(Order).where(
            Order.order_payment_key == qr_key,
            Order.order_status == "PENDING",
            Order.order_payment_status == "UNPAID",
            col(Order.order_created_date) <= older_than,
        )
    )
    return list(result.all())


# UC-26 / UC-27 — hóa đơn theo đơn (nếu đã xuất).
async def get_invoice_by_order(db: AsyncSession, order_key: UUID) -> Invoice | None:
    result = await db.exec(
        select(Invoice).where(Invoice.invoice_order_key == order_key)
    )
    return result.first()


# UC-26 — xuất hóa đơn khi giao thành công (snapshot).
async def create_invoice(
    db: AsyncSession, *, invoice_id: str, order_key: UUID, snapshot: dict[str, Any]
) -> Invoice:
    inv = Invoice(
        invoice_id=invoice_id,
        invoice_order_key=order_key,
        invoice_snapshot_json=snapshot,
    )
    db.add(inv)
    await db.flush()
    return inv


# UC-27 — xem hóa đơn theo invoice_id.
async def get_invoice_by_id(db: AsyncSession, invoice_id: str) -> Invoice | None:
    result = await db.exec(select(Invoice).where(Invoice.invoice_id == invoice_id))
    return result.first()
