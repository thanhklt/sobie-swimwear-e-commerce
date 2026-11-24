"""Ánh xạ các cột tồn kho, phiếu nhập và nhà cung cấp dùng cho UC-37."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Supplier(SQLModel, table=True):
    __tablename__ = "supplier"
    __table_args__ = {"schema": "inventory"}

    supplier_key: UUID = Field(primary_key=True)
    supplier_id: str = Field(max_length=10)
    supplier_name: str = Field(max_length=255)


class GoodsReceipt(SQLModel, table=True):
    __tablename__ = "goods_receipt"
    __table_args__ = {"schema": "inventory"}

    goods_receipt_key: UUID = Field(primary_key=True)
    goods_receipt_final_price: Decimal = Field(max_digits=12, decimal_places=0)
    goods_receipt_status: str = Field(max_length=20)
    goods_receipt_created_date: datetime = Field(sa_type=DateTime(timezone=True))
    goods_receipt_supplier_key: UUID = Field(
        foreign_key="inventory.supplier.supplier_key"
    )


class Stock(SQLModel, table=True):
    __tablename__ = "stock"
    __table_args__ = {"schema": "inventory"}

    stock_key: UUID = Field(primary_key=True)
    stock_variant_key: UUID
    stock_quantity: int
