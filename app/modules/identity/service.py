"""Tầng Service của module identity: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Lấy tài khoản và vai trò từ mã phiên trong cookie, gia hạn phiên (kiểm tra quyền mỗi request).
- Sổ địa chỉ giao hàng (UC-41): list / thêm / mặc định — cho ordering checkout.
- Kiểm tra tài khoản có vai trò Khách hàng (cho shopping) — khi sẵn sàng.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import TYPE_CHECKING
from uuid import UUID

from app.modules.identity import repository
from app.modules.identity.exceptions import (
    InvalidShippingAddressError,
    ShippingAddressNotFoundError,
)
from app.modules.identity.models import ShippingAddress
from app.modules.identity.schemas import ShippingAddressCreate, ShippingAddressView
from app.modules.identity.session import AuthenticatedSession, Role, SessionPortal
from app.shared.database.transaction import transaction

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

_SESSION_POLICIES = {
    SessionPortal.STOREFRONT: ((Role.CUSTOMER,), timedelta(minutes=30)),
    SessionPortal.PORTAL: ((Role.EMPLOYEE, Role.ADMIN), timedelta(hours=1)),
}


async def authenticate_session(
    token: str, portal: SessionPortal
) -> AuthenticatedSession | None:
    """Xác thực cookie phía server và gia hạn phiên còn hiệu lực."""
    if not token:
        return None

    from app.shared.database.engine import session_factory

    allowed_roles, lifetime = _SESSION_POLICIES[portal]
    seen_at = datetime.now(UTC)
    token_hash = sha256(token.encode("utf-8")).hexdigest()

    async with session_factory() as db, transaction(db):
        return await repository.renew_session(
            db,
            token_hash=token_hash,
            allowed_roles=allowed_roles,
            seen_at=seen_at,
            expires_at=seen_at + lifetime,
        )


def _require_address_fields(data: ShippingAddressCreate) -> None:
    fields = {
        "name": data.name,
        "phone": data.phone,
        "house_number": data.house_number,
        "ward": data.ward,
        "city": data.city,
        "country": data.country,
    }
    for key, value in fields.items():
        if not isinstance(value, str) or not value.strip():
            raise InvalidShippingAddressError(key)


def _to_view(row: ShippingAddress) -> ShippingAddressView:
    return ShippingAddressView(
        shipping_address_key=row.shipping_address_key,
        account_key=row.shipping_address_account_key,
        name=row.shipping_address_name,
        phone=row.shipping_address_phone,
        house_number=row.shipping_address_house_number,
        ward=row.shipping_address_ward,
        city=row.shipping_address_city,
        country=row.shipping_address_country,
        is_default=bool(row.shipping_address_is_default),
    )


async def list_shipping_addresses(
    db: AsyncSession, account_key: UUID
) -> list[ShippingAddressView]:
    rows = await repository.list_shipping_addresses(db, account_key)
    return [_to_view(row) for row in rows]


async def get_default_shipping_address(
    db: AsyncSession, account_key: UUID
) -> ShippingAddressView | None:
    row = await repository.get_default_shipping_address(db, account_key)
    return _to_view(row) if row else None


async def get_shipping_address(
    db: AsyncSession, *, account_key: UUID, address_key: UUID
) -> ShippingAddressView:
    row = await repository.get_shipping_address(
        db, account_key=account_key, address_key=address_key
    )
    if row is None:
        raise ShippingAddressNotFoundError()
    return _to_view(row)


async def add_shipping_address(
    db: AsyncSession, *, account_key: UUID, data: ShippingAddressCreate
) -> ShippingAddressView:
    """Thêm địa chỉ vào sổ. Địa chỉ đầu tiên tự mặc định (UC-41 AC-1/AC-2)."""
    _require_address_fields(data)
    async with transaction(db):
        count = await repository.count_shipping_addresses(db, account_key)
        is_default = count == 0
        row = await repository.insert_shipping_address(
            db,
            account_key=account_key,
            name=data.name.strip(),
            phone=data.phone.strip(),
            house_number=data.house_number.strip(),
            ward=data.ward.strip(),
            city=data.city.strip(),
            country=data.country.strip(),
            is_default=is_default,
        )
        if is_default:
            await repository.sync_account_address_mirror(
                db,
                account_key=account_key,
                house_number=row.shipping_address_house_number,
                ward=row.shipping_address_ward,
                city=row.shipping_address_city,
                country=row.shipping_address_country,
            )
        address_key = row.shipping_address_key

    loaded = await repository.get_shipping_address(
        db, account_key=account_key, address_key=address_key
    )
    assert loaded is not None
    return _to_view(loaded)


async def set_default_shipping_address(
    db: AsyncSession, *, account_key: UUID, address_key: UUID
) -> ShippingAddressView:
    """Đặt B làm mặc định; gỡ A trong cùng transaction (UC-41 AC-3)."""
    async with transaction(db):
        row = await repository.get_shipping_address(
            db, account_key=account_key, address_key=address_key
        )
        if row is None:
            raise ShippingAddressNotFoundError()
        if not row.shipping_address_is_default:
            await repository.clear_default_shipping_addresses(db, account_key)
            row = await repository.set_shipping_address_default(db, row)
        await repository.sync_account_address_mirror(
            db,
            account_key=account_key,
            house_number=row.shipping_address_house_number,
            ward=row.shipping_address_ward,
            city=row.shipping_address_city,
            country=row.shipping_address_country,
        )
        saved_key = row.shipping_address_key

    loaded = await repository.get_shipping_address(
        db, account_key=account_key, address_key=saved_key
    )
    assert loaded is not None
    return _to_view(loaded)
