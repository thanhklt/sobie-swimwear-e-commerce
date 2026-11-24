"""Ngoại lệ nghiệp vụ của module shopping."""

from __future__ import annotations


class ShoppingError(Exception):
    """Lỗi nghiệp vụ shopping."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InsufficientStockError(ShoppingError):
    """Số lượng vượt tồn kho (UC-18 E1 / AC-3)."""

    def __init__(self, available: int):
        super().__init__(f"Chỉ còn {available} sản phẩm")
        self.available = available


class InvalidQuantityError(ShoppingError):
    """Số lượng ≤ 0 hoặc không phải số nguyên dương (UC-18 E3)."""

    def __init__(self):
        super().__init__("Số lượng không hợp lệ")


class CartNotFoundError(ShoppingError):
    def __init__(self):
        super().__init__("Không tìm thấy giỏ hàng")


class CartItemNotFoundError(ShoppingError):
    def __init__(self):
        super().__init__("Không tìm thấy dòng giỏ hàng")


class WishlistNotFoundError(ShoppingError):
    def __init__(self):
        super().__init__("Không tìm thấy danh sách yêu thích")


class ProductNotFoundError(ShoppingError):
    """UC-38 E2."""

    def __init__(self):
        super().__init__("Không tìm thấy sản phẩm")


class MergeRequestConflictError(ShoppingError):
    """Cùng mã gộp nhưng payload khác (UC-18 E6)."""

    def __init__(self):
        super().__init__("Mã gộp không khớp dữ liệu đã lưu")
