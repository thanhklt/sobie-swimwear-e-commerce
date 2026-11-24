"""Kiểu dữ liệu công khai của module inventory, tách biệt với model lưu trữ."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PurchaseTotal:
    supplier_code: str
    supplier_name: str
    amount: int
