"""Model lưu trữ của module inventory (schema PostgreSQL `inventory`), theo
specs/entity-model/data_model_v2.dbml.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlmodel import Field, SQLModel


class Supplier(SQLModel, table=True):
    __tablename__ = "supplier"
    __table_args__ = (
        CheckConstraint("supplier_id ~ '^NCC-[0-9]{4}$'", name="supplier_supplier_id_ck"),
        CheckConstraint("supplier_status IN ('ACTIVE', 'INACTIVE')", name="supplier_status_ck"),
        {"schema": "inventory"},
    )

    supplier_key: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
    )
    supplier_id: str = Field(sa_column=Column(String(10), nullable=False, unique=True))
    supplier_name: str = Field(sa_column=Column(String(255), nullable=False))
    supplier_phone_number: str = Field(sa_column=Column(String(20), nullable=False))
    supplier_email: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))
    supplier_address: str | None = Field(default=None, sa_column=Column(String(255), nullable=True))
    supplier_status: str = Field(
        default="ACTIVE",
        sa_column=Column(String(20), nullable=False, server_default=text("'ACTIVE'")),
    )


class GoodsReceipt(SQLModel, table=True):
    __tablename__ = "goods_receipt"
    __table_args__ = (
        CheckConstraint("goods_receipt_id ~ '^PN-[0-9]{4}$'", name="goods_receipt_id_ck"),
        CheckConstraint("goods_receipt_final_price >= 0", name="goods_receipt_final_price_ck"),
        CheckConstraint(
            "goods_receipt_status IN ('DRAFT', 'CONFIRMED', 'CANCELLED')",
            name="goods_receipt_status_ck",
        ),
        {"schema": "inventory"},
    )

    goods_receipt_key: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
    )
    goods_receipt_id: str = Field(sa_column=Column(String(10), nullable=False, unique=True))
    goods_receipt_final_price: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 0), nullable=False, server_default=text("0")),
    )
    goods_receipt_status: str = Field(
        default="DRAFT",
        sa_column=Column(String(20), nullable=False, server_default=text("'DRAFT'")),
    )
    goods_receipt_created_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
    )
    goods_receipt_supplier_key: UUID = Field(
        sa_column=Column(
            Uuid(as_uuid=True),
            ForeignKey("inventory.supplier.supplier_key", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    goods_receipt_account_key: UUID = Field(
        sa_column=Column(
            Uuid(as_uuid=True),
            ForeignKey("identity.account.account_key", ondelete="RESTRICT"),
            nullable=False,
        )
    )


class GoodsReceiptDetail(SQLModel, table=True):
    __tablename__ = "goods_receipt_detail"
    __table_args__ = (
        CheckConstraint("goods_receipt_detail_quantity > 0", name="goods_receipt_detail_quantity_ck"),
        CheckConstraint("goods_receipt_detail_unit_price >= 0", name="goods_receipt_detail_unit_price_ck"),
        CheckConstraint(
            "goods_receipt_detail_total_price = goods_receipt_detail_quantity * goods_receipt_detail_unit_price",
            name="goods_receipt_detail_total_ck",
        ),
        UniqueConstraint(
            "goods_receipt_detail_goods_receipt_key",
            "goods_receipt_detail_variant_key",
            name="goods_receipt_detail_receipt_variant_uq",
        ),
        {"schema": "inventory"},
    )

    goods_receipt_detail_key: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
    )
    goods_receipt_detail_goods_receipt_key: UUID = Field(
        sa_column=Column(
            Uuid(as_uuid=True),
            ForeignKey("inventory.goods_receipt.goods_receipt_key", ondelete="CASCADE"),
            nullable=False,
        )
    )
    goods_receipt_detail_variant_key: UUID = Field(
        sa_column=Column(
            Uuid(as_uuid=True),
            ForeignKey("catalog.variant.variant_key", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    goods_receipt_detail_quantity: int = Field(sa_column=Column(Integer, nullable=False))
    goods_receipt_detail_unit_price: Decimal = Field(sa_column=Column(Numeric(12, 0), nullable=False))
    goods_receipt_detail_total_price: Decimal = Field(sa_column=Column(Numeric(12, 0), nullable=False))


class Stock(SQLModel, table=True):
    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="stock_quantity_ck"),  # tồn kho không bao giờ âm
        CheckConstraint("stock_cost_price >= 0", name="stock_cost_price_ck"),
        {"schema": "inventory"},
    )

    stock_key: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
    )
    stock_variant_key: UUID = Field(
        sa_column=Column(
            Uuid(as_uuid=True),
            ForeignKey("catalog.variant.variant_key", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        )
    )
    stock_quantity: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
    )
    stock_cost_price: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 0), nullable=False, server_default=text("0")),
    )
