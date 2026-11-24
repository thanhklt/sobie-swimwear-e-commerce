"""Kiểu dữ liệu công khai của module catalog, tách biệt với model lưu trữ."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VariantSummary:
    sku: str
    product_code: str
    product_name: str
    sell_price: int | None
