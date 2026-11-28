"""Tầng Repository của module identity: truy vấn các bảng do module sở hữu:
- identity.role
- identity.account
- identity.session
- identity.shipping_address

Không truy vấn bảng của module khác.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, bindparam, text
from sqlmodel import col, select

from app.modules.identity.models import ShippingAddress
from app.modules.identity.session import AuthenticatedSession, Role

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


_RENEW_SESSION = text(
    """
    WITH eligible_session AS (
        SELECT account.account_key, role.role_code
        FROM identity.session AS candidate
        JOIN identity.account AS account ON account.account_key = candidate.session_account_key
        JOIN identity.role AS role ON role.role_key = account.account_role_key
        WHERE candidate.session_token_hash = :token_hash
          AND account.account_status = 'ACTIVE'
          AND role.role_code IN :allowed_roles
    )
    UPDATE identity.session
    SET session_last_seen_at = CASE
            WHEN session_last_seen_at < :seen_at THEN :seen_at
            ELSE session_last_seen_at
        END,
        session_expires_at = CASE
            WHEN session_last_seen_at < :seen_at THEN :expires_at
            ELSE session_expires_at
        END
    WHERE session_token_hash = :token_hash
      AND session_expires_at > :seen_at
      AND session_account_key IN (SELECT account_key FROM eligible_session)
    RETURNING session_key, session_account_key,
        (SELECT role_code FROM eligible_session) AS role_code
    """
).bindparams(
    bindparam("allowed_roles", expanding=True),
    bindparam("seen_at", type_=DateTime(timezone=True)),
    bindparam("expires_at", type_=DateTime(timezone=True)),
)


# UC-02 — gia hạn phiên đăng nhập còn hạn (cookie / authenticate_session).
async def renew_session(
    db: AsyncSession,
    *,
    token_hash: str,
    allowed_roles: tuple[Role, ...],
    seen_at: datetime,
    expires_at: datetime,
) -> AuthenticatedSession | None:
    """Gia hạn nguyên tử phiên còn hạn thuộc tài khoản và cổng hợp lệ."""
    result = await db.exec(
        _RENEW_SESSION,
        params={
            "token_hash": token_hash,
            "allowed_roles": tuple(role.value for role in allowed_roles),
            "seen_at": seen_at,
            "expires_at": expires_at,
        },
    )
    row = result.mappings().one_or_none()
    if row is None:
        return None

    return AuthenticatedSession(
        session_key=UUID(str(row["session_key"])),
        account_key=UUID(str(row["session_account_key"])),
        role=Role(row["role_code"]),
    )


# UC-41 Main Flow bước 1–2 — liệt kê sổ địa chỉ (dùng thêm UC-19/UC-20 checkout).
async def list_shipping_addresses(
    db: AsyncSession, account_key: UUID
) -> list[ShippingAddress]:
    result = await db.exec(
        select(ShippingAddress)
        .where(ShippingAddress.shipping_address_account_key == account_key)
        .order_by(
            col(ShippingAddress.shipping_address_is_default).desc(),
            col(ShippingAddress.shipping_address_created_at).asc(),
            col(ShippingAddress.shipping_address_key).asc(),
        )
    )
    return list(result.all())


# UC-41 — lấy 1 địa chỉ thuộc tài khoản (UC-19/UC-20 chọn địa chỉ đặt hàng; E2).
async def get_shipping_address(
    db: AsyncSession, *, account_key: UUID, address_key: UUID
) -> ShippingAddress | None:
    result = await db.exec(
        select(ShippingAddress).where(
            ShippingAddress.shipping_address_key == address_key,
            ShippingAddress.shipping_address_account_key == account_key,
        )
    )
    return result.first()


# UC-41 — địa chỉ mặc định; UC-19 AC-12 / UC-20 prefill checkout.
async def get_default_shipping_address(
    db: AsyncSession, account_key: UUID
) -> ShippingAddress | None:
    result = await db.exec(
        select(ShippingAddress).where(
            ShippingAddress.shipping_address_account_key == account_key,
            col(ShippingAddress.shipping_address_is_default) == True,  # noqa: E712
        )
    )
    return result.first()


# UC-41 AC-1 / AC-2 — đếm để quyết định địa chỉ đầu = mặc định.
async def count_shipping_addresses(db: AsyncSession, account_key: UUID) -> int:
    rows = await list_shipping_addresses(db, account_key)
    return len(rows)


# UC-41 AC-1 / AC-2 / AC-4 — thêm dòng sổ; UC-19 AC-13 thêm tại checkout.
async def insert_shipping_address(
    db: AsyncSession,
    *,
    account_key: UUID,
    name: str,
    phone: str,
    house_number: str,
    ward: str,
    city: str,
    country: str,
    is_default: bool,
) -> ShippingAddress:
    now = datetime.now(UTC)
    row = ShippingAddress(
        shipping_address_account_key=account_key,
        shipping_address_name=name,
        shipping_address_phone=phone,
        shipping_address_house_number=house_number,
        shipping_address_ward=ward,
        shipping_address_city=city,
        shipping_address_country=country,
        shipping_address_is_default=is_default,
        shipping_address_created_at=now,
        shipping_address_updated_at=now,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


# UC-41 AC-3 — gỡ is_default của A trước khi đặt B làm mặc định.
async def clear_default_shipping_addresses(
    db: AsyncSession, account_key: UUID
) -> None:
    rows = await list_shipping_addresses(db, account_key)
    now = datetime.now(UTC)
    for row in rows:
        if row.shipping_address_is_default:
            row.shipping_address_is_default = False
            row.shipping_address_updated_at = now
            db.add(row)
    await db.flush()


# UC-41 AC-3 — gán is_default = true cho địa chỉ B.
async def set_shipping_address_default(
    db: AsyncSession, address: ShippingAddress
) -> ShippingAddress:
    now = datetime.now(UTC)
    address.shipping_address_is_default = True
    address.shipping_address_updated_at = now
    db.add(address)
    await db.flush()
    await db.refresh(address)
    return address


_UPDATE_ACCOUNT_ADDRESS_MIRROR = text(
    """
    UPDATE identity.account
    SET account_house_number = :house_number,
        account_ward = :ward,
        account_city = :city,
        account_country = :country
    WHERE account_key = :account_key
    """
)


# UC-41 AC-1 / AC-3 + BR-001 — mirror địa chỉ mặc định lên identity.account.
async def sync_account_address_mirror(
    db: AsyncSession,
    *,
    account_key: UUID,
    house_number: str,
    ward: str,
    city: str,
    country: str,
) -> None:
    """Đồng bộ cột địa chỉ trên account = địa chỉ mặc định (BR-001)."""
    await db.exec(
        _UPDATE_ACCOUNT_ADDRESS_MIRROR.bindparams(
            account_key=account_key,
            house_number=house_number,
            ward=ward,
            city=city,
            country=country,
        )
    )
    await db.flush()
