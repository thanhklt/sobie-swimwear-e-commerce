"""Tiện ích tính VND bằng số nguyên và Decimal, ROUND_HALF_UP."""

from decimal import Decimal, ROUND_HALF_UP


def percent_of(amount: int, percentage: Decimal) -> int:
    if amount < 0:
        raise ValueError("Số tiền không được âm.")
    value = Decimal(amount) * Decimal(percentage) / Decimal(100)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def discounted_price(amount: int, percentage: Decimal) -> int:
    value = Decimal(amount) * (Decimal(100) - Decimal(percentage)) / Decimal(100)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
