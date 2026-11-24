"""UC-18 — gộp giỏ (AC-6, AC-9, AC-10, AC-11)."""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.shopping import service
from app.modules.shopping.exceptions import MergeRequestConflictError
from app.modules.shopping.schemas import GuestCartLine
from app.shared.database.engine import session_factory
from tests.shopping.conftest import DemoIds, availability_for, db_cart_qty, set_stock
from tests.shopping.fakes import FakeAvailability


@pytest.mark.asyncio
async def test_uc18_ac6_merge_cart_capped_by_stock(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    await set_stock(db, demo.variant_do_m, 3)
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=2,
        availability=availability_for(demo.variant_do_m, 3),
    )
    result = await service.merge_guest_cart(
        db,
        account_key=demo.account_key,
        merge_id=str(uuid4()),
        guest_lines=[GuestCartLine(variant_key=demo.variant_do_m, quantity=2)],
        availability=availability_for(demo.variant_do_m, 3),
    )
    assert result[demo.variant_do_m] == 3
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 3


@pytest.mark.asyncio
async def test_uc18_ac9_merge_when_stock_lower_than_guest(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    await set_stock(db, demo.variant_do_m, 1)
    result = await service.merge_guest_cart(
        db,
        account_key=demo.account_key,
        merge_id=str(uuid4()),
        guest_lines=[GuestCartLine(variant_key=demo.variant_do_m, quantity=2)],
        availability=availability_for(demo.variant_do_m, 1),
    )
    assert result[demo.variant_do_m] == 1
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 1


@pytest.mark.asyncio
async def test_uc18_ac10_merge_retry_same_id_no_double_count(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    await set_stock(db, demo.variant_do_m, 10)
    await service.add_item_to_cart(
        db,
        account_key=demo.account_key,
        variant_key=demo.variant_do_m,
        quantity=1,
        availability=availability_for(demo.variant_do_m, 10),
    )
    merge_id = "merge-M-ac10"
    guest = [GuestCartLine(variant_key=demo.variant_do_m, quantity=2)]
    avail = availability_for(demo.variant_do_m, 10)

    first = await service.merge_guest_cart(
        db,
        account_key=demo.account_key,
        merge_id=merge_id,
        guest_lines=guest,
        availability=avail,
    )
    assert first[demo.variant_do_m] == 3

    second = await service.merge_guest_cart(
        db,
        account_key=demo.account_key,
        merge_id=merge_id,
        guest_lines=guest,
        availability=avail,
    )
    assert second[demo.variant_do_m] == 3
    assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 3


@pytest.mark.asyncio
async def test_uc18_ac10_merge_same_id_different_payload_rejected(
    db: AsyncSession, demo: DemoIds, clean_cart: None
) -> None:
    await set_stock(db, demo.variant_do_m, 10)
    merge_id = "merge-M-conflict"
    await service.merge_guest_cart(
        db,
        account_key=demo.account_key,
        merge_id=merge_id,
        guest_lines=[GuestCartLine(variant_key=demo.variant_do_m, quantity=1)],
        availability=availability_for(demo.variant_do_m, 10),
    )
    with pytest.raises(MergeRequestConflictError):
        await service.merge_guest_cart(
            db,
            account_key=demo.account_key,
            merge_id=merge_id,
            guest_lines=[GuestCartLine(variant_key=demo.variant_do_m, quantity=2)],
            availability=availability_for(demo.variant_do_m, 10),
        )


@pytest.mark.asyncio
async def test_uc18_ac11_concurrent_same_merge_applied_once(
    demo: DemoIds, clean_cart: None
) -> None:
    async with session_factory() as setup:
        await set_stock(setup, demo.variant_do_m, 10)
        await service.add_item_to_cart(
            setup,
            account_key=demo.account_key,
            variant_key=demo.variant_do_m,
            quantity=1,
            availability=availability_for(demo.variant_do_m, 10),
        )

    merge_id = "merge-concurrent-ac11"
    guest = [GuestCartLine(variant_key=demo.variant_do_m, quantity=2)]

    async def one_merge() -> dict[UUID, int]:
        async with session_factory() as db:
            return await service.merge_guest_cart(
                db,
                account_key=demo.account_key,
                merge_id=merge_id,
                guest_lines=guest,
                availability=FakeAvailability({demo.variant_do_m: 10}),
            )

    results = await asyncio.gather(one_merge(), one_merge(), return_exceptions=True)
    successes = [r for r in results if isinstance(r, dict)]
    assert len(successes) >= 1
    async with session_factory() as db:
        assert await db_cart_qty(db, demo.account_key, demo.variant_do_m) == 3
    for s in successes:
        assert s[demo.variant_do_m] == 3
