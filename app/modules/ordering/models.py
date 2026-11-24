"""Ánh xạ các cột đơn hàng và lịch sử dùng cho truy vấn UC-09 và UC-37."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    __tablename__ = "order"
    __table_args__ = {"schema": "ordering"}

    order_key: UUID = Field(primary_key=True)
    order_total_price: Decimal = Field(max_digits=12, decimal_places=0)
    order_shipping_fee: Decimal = Field(max_digits=12, decimal_places=0)
    order_status: str = Field(max_length=20)
    order_created_date: datetime = Field(sa_type=DateTime(timezone=True))


class OrderDetail(SQLModel, table=True):
    __tablename__ = "order_detail"
    __table_args__ = {"schema": "ordering"}

    order_detail_key: UUID = Field(primary_key=True)
    order_detail_order_key: UUID = Field(foreign_key="ordering.order.order_key")
    order_detail_variant_key: UUID
    order_detail_quantity: int
    order_detail_cost_price: Decimal = Field(max_digits=12, decimal_places=0)


class OrderStatusHistory(SQLModel, table=True):
    __tablename__ = "order_status_history"
    __table_args__ = {"schema": "ordering"}

    order_status_history_key: UUID = Field(primary_key=True)
    order_status_history_order_key: UUID = Field(foreign_key="ordering.order.order_key")
    order_status_history_to_value: str = Field(max_length=20)
    order_status_history_changed_time: datetime = Field(sa_type=DateTime(timezone=True))
