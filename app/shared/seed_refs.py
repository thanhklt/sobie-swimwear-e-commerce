"""SQLModel tạm [GD] map bảng identity/catalog/inventory cho adapter UI + test.

Shopping và ordering cùng đọc seed — chỉ định nghĩa Table một lần trên MetaData.
Thay bằng service công khai khi teammate catalog/inventory/identity sẵn sàng.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, SQLModel


class AccountRef(SQLModel, table=True):
    __tablename__ = "account"
    __table_args__ = {"schema": "identity"}

    account_key: UUID = Field(primary_key=True)
    account_email: str = Field(max_length=255, unique=True)


class StockRef(SQLModel, table=True):
    __tablename__ = "stock"
    __table_args__ = {"schema": "inventory"}

    stock_key: UUID = Field(default_factory=uuid4, primary_key=True)
    stock_variant_key: UUID = Field(unique=True, index=True)
    stock_quantity: int = Field(default=0, ge=0)
    stock_cost_price: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 0), nullable=False, server_default="0"),
    )


class VariantRef(SQLModel, table=True):
    __tablename__ = "variant"
    __table_args__ = {"schema": "catalog"}

    variant_key: UUID = Field(primary_key=True)
    variant_id: str = Field(max_length=60, unique=True)
    variant_product_key: UUID = Field(index=True)
    variant_size_key: UUID
    variant_color_key: UUID
    variant_sell_price: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(12, 0), nullable=True),
    )


class ProductRef(SQLModel, table=True):
    __tablename__ = "product"
    __table_args__ = {"schema": "catalog"}

    product_key: UUID = Field(primary_key=True)
    product_id: str = Field(max_length=10, unique=True)
    product_name: str = Field(max_length=255)
    product_status: str = Field(max_length=20, default="INACTIVE")


class ColorRef(SQLModel, table=True):
    __tablename__ = "color"
    __table_args__ = {"schema": "catalog"}

    color_key: UUID = Field(primary_key=True)
    color_name: str = Field(max_length=50)


class SizeRef(SQLModel, table=True):
    __tablename__ = "size"
    __table_args__ = {"schema": "catalog"}

    size_key: UUID = Field(primary_key=True)
    size_name: str = Field(max_length=50)


class GalleryRef(SQLModel, table=True):
    __tablename__ = "gallery"
    __table_args__ = {"schema": "catalog"}

    gallery_key: UUID = Field(primary_key=True)
    gallery_product_key: UUID = Field(index=True)
    gallery_order_no: int
    gallery_url: str = Field(max_length=500)
