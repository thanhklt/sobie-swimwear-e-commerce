"""SQLModel — schema PostgreSQL `ordering`."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Payment(SQLModel, table=True):
    __tablename__ = "payment"
    __table_args__ = {"schema": "ordering"}

    payment_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    payment_name: str = Field(max_length=100, unique=True)


class Order(SQLModel, table=True):
    __tablename__ = "order"
    __table_args__ = {"schema": "ordering"}

    order_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    order_code: str = Field(max_length=8, unique=True, index=True)
    order_account_key: UUID = Field(index=True)
    order_payment_key: UUID
    order_order_promotion_key: UUID | None = None
    order_code_promotion_key: UUID | None = None
    order_customer_name: str = Field(max_length=255)
    order_customer_phone_number: str = Field(max_length=20)
    order_customer_house_number: str = Field(max_length=255)
    order_customer_ward: str = Field(max_length=100)
    order_customer_city: str = Field(max_length=255)
    order_customer_country: str = Field(max_length=100)
    order_discount_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 0), nullable=False, server_default="0"),
    )
    order_shipping_fee: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False),
    )
    order_total_price: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False),
    )
    order_payment_status: str = Field(default="UNPAID", max_length=20)
    order_status: str = Field(default="PENDING", max_length=20)
    order_created_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    order_updated_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )


class OrderDetail(SQLModel, table=True):
    __tablename__ = "order_detail"
    __table_args__ = (
        UniqueConstraint(
            "order_detail_order_key",
            "order_detail_variant_key",
            name="order_detail_order_variant_uq",
        ),
        {"schema": "ordering"},
    )

    order_detail_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    order_detail_order_key: UUID = Field(index=True)
    order_detail_variant_key: UUID
    order_detail_quantity: int = Field(gt=0)
    order_detail_unit_price: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False),
    )
    order_detail_product_promotion_key: UUID | None = None
    order_detail_cost_price: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False),
    )


class OrderStatusHistory(SQLModel, table=True):
    __tablename__ = "order_status_history"
    __table_args__ = {"schema": "ordering"}

    order_status_history_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    order_status_history_order_key: UUID = Field(index=True)
    order_status_history_from_value: str | None = Field(default=None, max_length=20)
    order_status_history_to_value: str = Field(max_length=20)
    order_status_history_source: str = Field(max_length=20)
    order_status_history_note: str | None = None
    order_status_history_changed_by_key: UUID | None = None
    order_status_history_changed_time: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )


class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"
    __table_args__ = {"schema": "ordering"}

    invoice_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    invoice_id: str = Field(max_length=11, unique=True)
    invoice_order_key: UUID = Field(unique=True)
    invoice_created_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    invoice_snapshot_json: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
