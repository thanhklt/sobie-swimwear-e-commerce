"""Ánh xạ các cột của catalog dùng cho truy vấn báo cáo UC-09 và UC-37."""

from decimal import Decimal
from uuid import UUID

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "product"
    __table_args__ = {"schema": "catalog"}

    product_key: UUID = Field(primary_key=True)
    product_id: str = Field(max_length=10)
    product_name: str = Field(max_length=255)


class ProductVariant(SQLModel, table=True):
    __tablename__ = "variant"
    __table_args__ = {"schema": "catalog"}

    variant_key: UUID = Field(primary_key=True)
    variant_id: str = Field(max_length=60)
    variant_product_key: UUID = Field(foreign_key="catalog.product.product_key")
    variant_sell_price: Decimal | None = Field(
        default=None, max_digits=12, decimal_places=0
    )
