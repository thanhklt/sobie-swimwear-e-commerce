"""SQLModel cho schema promotion — khớp data model v2 / infra/postgres/init.sql.

Bảng do init.sql tạo sẵn; module không gọi metadata.create_all.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field, SQLModel


class Promotion(SQLModel, table=True):
    __tablename__ = "promotion"
    __table_args__ = {"schema": "promotion"}

    promotion_key: UUID = Field(default_factory=uuid4, primary_key=True)
    promotion_id: str = Field(max_length=10, unique=True, index=True)
    promotion_type: str = Field(max_length=20)
    promotion_quantity: Optional[int] = Field(default=None)
    promotion_used_amount: int = Field(default=0)
    promotion_start_date: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    promotion_end_date: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    promotion_status: str = Field(default="ENABLED", max_length=20)


class ProductPromotion(SQLModel, table=True):
    __tablename__ = "product_promotion"
    __table_args__ = {"schema": "promotion"}

    promotion_key: UUID = Field(primary_key=True, foreign_key="promotion.promotion.promotion_key")
    product_promotion_product_key: UUID
    product_promotion_discount_percentage: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False)
    )


class OrderPromotion(SQLModel, table=True):
    __tablename__ = "order_promotion"
    __table_args__ = {"schema": "promotion"}

    promotion_key: UUID = Field(primary_key=True, foreign_key="promotion.promotion.promotion_key")
    order_promotion_discount_percentage: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False)
    )
    order_promotion_thresh_price: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False)
    )


class CodePromotion(SQLModel, table=True):
    __tablename__ = "code_promotion"
    __table_args__ = {"schema": "promotion"}

    promotion_key: UUID = Field(primary_key=True, foreign_key="promotion.promotion.promotion_key")
    code_promotion_code: str = Field(max_length=50, unique=True)
    code_promotion_discount_percentage: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False)
    )
    code_promotion_thresh_price: Decimal = Field(
        sa_column=Column(Numeric(12, 0), nullable=False)
    )


__all__ = [
    "Promotion",
    "ProductPromotion",
    "OrderPromotion",
    "CodePromotion",
]
