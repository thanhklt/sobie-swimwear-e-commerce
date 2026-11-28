"""DTO ordering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StatusHistoryView:
    """Một mốc đổi trạng thái đơn (order_status_history)."""

    from_status: str | None
    to_status: str
    source: str
    changed_at: datetime
    note: str | None  # chỉ điền khi NV xem; KH luôn None
    # Nhãn tiếng Việt cho KH (vd. "Cửa hàng đã xác nhận", "Đã hủy")
    event_label: str = ""
    status_label: str = ""  # nhãn của to_status


@dataclass(frozen=True, slots=True)
class ShippingInfo:
    name: str
    phone: str
    house_number: str
    ward: str
    city: str
    country: str


@dataclass(frozen=True, slots=True)
class OrderLineQuote:
    variant_key: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    cost_price: Decimal
    product_promotion_key: UUID | None = None


@dataclass(frozen=True, slots=True)
class OrderQuote:
    lines: tuple[OrderLineQuote, ...]
    subtotal: Decimal
    discount_amount: Decimal
    shipping_fee: Decimal
    total_price: Decimal
    order_promotion_key: UUID | None
    code_promotion_key: UUID | None


@dataclass(frozen=True, slots=True)
class OrderView:
    order_key: UUID
    order_code: str
    account_key: UUID
    payment_name: str
    status: str
    payment_status: str
    discount_amount: Decimal
    shipping_fee: Decimal
    total_price: Decimal
    customer_name: str
    customer_phone: str
    created_at: datetime
    payment_deadline: datetime | None  # QR: created + 24h
    show_qr: bool
    transfer_content: str | None  # SOBIE + code
    # VietQR hiển thị (UC-20) — chỉ có khi show_qr
    bank_id: str | None = None
    bank_account_no: str | None = None
    bank_account_name: str | None = None
    vietqr_image_url: str | None = None
    # Lịch sử trạng thái — chỉ nạp khi xem chi tiết đơn
    status_history: tuple[StatusHistoryView, ...] = field(default_factory=tuple)
    # Nhãn tiếng Việt hiện UI (code status vẫn giữ trong `status`)
    status_label: str = ""


@dataclass(frozen=True, slots=True)
class InvoiceView:
    invoice_id: str
    order_code: str
    created_at: datetime
    snapshot: dict
