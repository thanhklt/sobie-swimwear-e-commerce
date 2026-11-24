"""Model lưu trữ SQLModel của module shopping (schema PostgreSQL `shopping`)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, UniqueConstraint, func, text
from sqlmodel import Field, SQLModel


class Cart(SQLModel, table=True):
    __tablename__ = "cart"
    __table_args__ = {"schema": "shopping"}

    cart_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    cart_account_key: UUID = Field(unique=True, index=True)


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_item"
    __table_args__ = (
        UniqueConstraint(
            "cart_item_cart_key",
            "cart_item_variant_key",
            name="cart_item_cart_variant_uq",
        ),
        {"schema": "shopping"},
    )

    cart_item_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    cart_item_cart_key: UUID = Field(index=True)
    cart_item_variant_key: UUID = Field(index=True)
    cart_item_quantity: int = Field(default=1, ge=1)


class Wishlist(SQLModel, table=True):
    __tablename__ = "wishlist"
    __table_args__ = {"schema": "shopping"}

    wishlist_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    wishlist_account_key: UUID = Field(unique=True, index=True)


class WishlistItem(SQLModel, table=True):
    __tablename__ = "wishlist_item"
    __table_args__ = (
        UniqueConstraint(
            "wishlist_item_wishlist_key",
            "wishlist_item_product_key",
            name="wishlist_item_wishlist_product_uq",
        ),
        {"schema": "shopping"},
    )

    wishlist_item_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    wishlist_item_wishlist_key: UUID = Field(index=True)
    wishlist_item_product_key: UUID = Field(index=True)
    # [GD] UC-38 AC-3
    wishlist_item_added_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


class CartMergeRequest(SQLModel, table=True):
    """[GD] UC-18 AC-10/AC-11 — chống cộng trùng khi gộp giỏ."""

    __tablename__ = "cart_merge_request"
    __table_args__ = (
        UniqueConstraint(
            "cart_merge_request_account_key",
            "cart_merge_request_id",
            name="cart_merge_request_account_id_uq",
        ),
        {"schema": "shopping"},
    )

    cart_merge_request_key: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    cart_merge_request_account_key: UUID = Field(index=True)
    cart_merge_request_id: str = Field(max_length=64)
    cart_merge_request_payload_hash: str = Field(max_length=64)
    cart_merge_request_created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
