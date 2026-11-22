"""Quản lý transaction dùng chung.

Các thao tác đi qua nhiều module (trừ tồn + áp khuyến mãi + tạo đơn; ghi giao dịch SePay +
đánh dấu đơn đã thanh toán) phải chạy trong cùng 1 transaction: service của module gọi
truyền cùng session cho service của module được gọi.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Mở transaction trên session chưa có transaction đang hoạt động.

    Service điều phối truyền cùng session cho các service tham gia. Transaction
    commit khi khối kết thúc thành công và rollback khi có ngoại lệ. Bên gọi
    chịu trách nhiệm đóng session.
    """
    async with session.begin():
        yield session
