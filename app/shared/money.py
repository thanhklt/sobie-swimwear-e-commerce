"""Tiện ích tiền tệ: số nguyên VND / Decimal, làm tròn ROUND_HALF_UP; không dùng float."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

_VND = Decimal("1")


def to_vnd(amount: Decimal | int | str) -> Decimal:
    """Chuẩn hóa số tiền về số nguyên VND (ROUND_HALF_UP)."""
    return Decimal(amount).quantize(_VND, rounding=ROUND_HALF_UP)


def line_amount(unit_price: Decimal | int, quantity: int) -> Decimal:
    """Thành tiền một dòng = đơn giá × số lượng, làm tròn VND."""
    if quantity < 0:
        raise ValueError("quantity phải >= 0")
    return to_vnd(Decimal(unit_price) * quantity)
