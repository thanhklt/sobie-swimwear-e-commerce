"""SQLModel — schema PostgreSQL `identity` (bảng đã triển khai trong code).

shipping_address: UC-41. account/session vẫn truy vấn qua repository (SQL) để
tránh trùng MetaData với AccountRef tạm [GD] ở app.shared.seed_refs.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, func, text
from sqlmodel import Field, SQLModel


class ShippingAddress(SQLModel, table=True):
    __tablename__ = "shipping_address"
    __table_args__ = {"schema": "identity"}

    shipping_address_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    shipping_address_account_key: UUID = Field(index=True)
    shipping_address_name: str = Field(max_length=255)
    shipping_address_phone: str = Field(max_length=20)
    shipping_address_house_number: str = Field(max_length=255)
    shipping_address_ward: str = Field(max_length=100)
    shipping_address_city: str = Field(max_length=255)
    shipping_address_country: str = Field(max_length=100)
    shipping_address_is_default: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    shipping_address_created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    shipping_address_updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
