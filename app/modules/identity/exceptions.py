"""Ngoại lệ nghiệp vụ module identity."""

from __future__ import annotations


class IdentityError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ShippingAddressNotFoundError(IdentityError):
    def __init__(self):
        super().__init__("Không tìm thấy địa chỉ giao hàng")


class InvalidShippingAddressError(IdentityError):
    def __init__(self, field: str):
        labels = {
            "name": "họ tên người nhận",
            "phone": "số điện thoại",
            "house_number": "số nhà / đường",
            "ward": "phường / xã",
            "city": "tỉnh / thành",
            "country": "quốc gia",
        }
        super().__init__(f"Thiếu hoặc không hợp lệ: {labels.get(field, field)}")
        self.field = field
