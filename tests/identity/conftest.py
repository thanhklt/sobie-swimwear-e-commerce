"""Fixture identity — PostgreSQL docker."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.identity import repository, service
from app.modules.identity.schemas import ShippingAddressCreate
from app.modules.shopping.adapters import DEMO_EMAIL, get_account_key_by_email
from app.shared.database.engine import session_factory


@dataclass(frozen=True, slots=True)
class DemoIds:
    account_key: UUID


@pytest_asyncio.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
        if session.in_transaction():
            await session.rollback()


@pytest_asyncio.fixture
async def demo(db: AsyncSession) -> DemoIds:
    return DemoIds(account_key=await get_account_key_by_email(db, DEMO_EMAIL))


@pytest_asyncio.fixture
async def reset_addresses(db: AsyncSession, demo: DemoIds) -> None:
    """Mỗi test bắt đầu với đúng 1 địa chỉ mặc định (giống seed)."""
    rows = await repository.list_shipping_addresses(db, demo.account_key)
    for row in rows:
        await db.delete(row)
    await db.commit()
    await service.add_shipping_address(
        db,
        account_key=demo.account_key,
        data=ShippingAddressCreate(
            name="Khách Hàng Demo",
            phone="0900000003",
            house_number="273 An Dương Vương",
            ward="Phường Chợ Quán",
            city="TP. Hồ Chí Minh",
            country="Việt Nam",
        ),
    )
