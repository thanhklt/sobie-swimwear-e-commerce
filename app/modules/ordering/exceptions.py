"""Ngoại lệ nghiệp vụ module ordering."""

from __future__ import annotations

from decimal import Decimal


class OrderingError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EmptyCartError(OrderingError):
    def __init__(self):
        super().__init__("Giỏ hàng không có sản phẩm có thể đặt")


class InsufficientStockError(OrderingError):
    def __init__(self, variant_key: str | None = None):
        msg = "Không đủ tồn kho"
        if variant_key:
            msg = f"Không đủ tồn kho cho biến thể {variant_key}"
        super().__init__(msg)
        self.variant_key = variant_key


class MissingShippingInfoError(OrderingError):
    def __init__(self, field: str):
        labels = {
            "name": "họ tên",
            "phone": "số điện thoại",
            "house_number": "địa chỉ",
            "ward": "phường/xã",
            "city": "tỉnh/thành",
            "country": "quốc gia",
        }
        super().__init__(f"Thiếu {labels.get(field, field)}")
        self.field = field


class PriceChangedError(OrderingError):
    """UC-19 AC-9 / UC-20 AC-8: tổng đổi → yêu cầu xác nhận lại."""

    def __init__(self, new_total: Decimal):
        super().__init__("Giá hoặc khuyến mãi đã thay đổi, vui lòng xác nhận lại")
        self.new_total = new_total


class OrderNotFoundError(OrderingError):
    def __init__(self):
        super().__init__("Không tìm thấy đơn hàng")


class InvalidOrderStateError(OrderingError):
    def __init__(self, message: str = "Trạng thái đơn không hợp lệ cho thao tác này"):
        super().__init__(message)


class UnpaidQrConfirmError(OrderingError):
    def __init__(self):
        super().__init__("Đơn chưa được thanh toán")


class CancelNotAllowedError(OrderingError):
    def __init__(self, message: str = "Không thể hủy đơn ở trạng thái hiện tại"):
        super().__init__(message)


class InvalidCancelReasonError(OrderingError):
    def __init__(self):
        super().__init__("Lý do hủy không hợp lệ")
