"""Public shipping workflows delegated to the ordering module."""

from __future__ import annotations

from app.modules.ordering import service as ordering_service
from app.modules.shipping.schemas import ShippingActionRequest, ShippingOrderView
from pydantic import ValidationError


def _match_order_code(order_code: str, query: str | None) -> bool:
    if not query:
        return True
    needle = query.strip().upper()
    if not needle:
        return True
    hay = order_code.upper()
    return hay == needle or needle in hay


async def list_simulator_orders(db, *, q: str | None = None, status: str | None = None):
    """Return only public order codes and statuses for UC-36, optionally filtered."""
    rows = await ordering_service.list_shipping_orders(db)
    views = [ShippingOrderView.model_validate(row).model_dump() for row in rows]
    if status in {"AWAITING_PICKUP", "SHIPPING"}:
        views = [row for row in views if row["status"] == status]
    if q:
        views = [row for row in views if _match_order_code(row["order_code"], q)]
    return views


async def update_simulator_status(db, order_code: str, action: str) -> str:
    """Apply a carrier status transition through the ordering service."""
    try:
        request = ShippingActionRequest(action=action)
    except ValidationError as exc:
        raise ValueError("Thao tác giao hàng không hợp lệ.") from exc
    return await ordering_service.update_shipping_status(db, order_code, request.action)


async def list_orders_ready_for_handoff(db, *, q: str | None = None):
    """Return confirmed orders that employees can hand to a carrier."""
    rows = await ordering_service.list_confirmed_orders(db)
    if q:
        rows = [row for row in rows if _match_order_code(row["order_code"], q)]
    return rows


async def handoff_order(db, order_code: str, employee_key) -> bool:
    """Hand one confirmed order to shipping and record its history.

    Propagates distinct errors from ordering:
    - LookupError → E2 không tìm thấy đơn
    - ValueError → E1 báo trạng thái thực tế
    """
    return await ordering_service.handoff_order(db, order_code, employee_key)
