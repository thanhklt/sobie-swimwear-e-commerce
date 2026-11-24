"""Tầng Service của module shopping: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Khởi tạo giỏ hàng và danh sách yêu thích của tài khoản Khách hàng.
- Đọc các dòng giỏ của khách (cho ordering khi đặt hàng).
- Xóa các dòng đã đặt khỏi giỏ sau khi tạo đơn.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from app.modules.shopping import repository

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


# UC-01 Đăng ký tài khoản — Main 7; 1b.4; E6 (specs/use-cases/identity/UC-01-register-account.md)
async def initialize_customer_shopping(db: "AsyncSession", *, account_key: UUID) -> None:
    await repository.insert_cart(db, account_key=account_key)
    await repository.insert_wishlist(db, account_key=account_key)
