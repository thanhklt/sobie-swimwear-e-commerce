"""SQLModel mappings for the identity schema."""
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, SQLModel


class IdentityRole(SQLModel, table=True):
    __tablename__ = "role"
    __table_args__ = {"schema": "identity"}

    role_key: UUID | None = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    role_code: str = Field(max_length=50, unique=True)
    role_name: str = Field(max_length=100, unique=True)


class IdentityAccount(SQLModel, table=True):
    __tablename__ = "account"
    __table_args__ = {"schema": "identity"}

    account_key: UUID | None = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    account_id: str = Field(max_length=100, unique=True)
    account_role_key: UUID = Field(foreign_key="identity.role.role_key")
    account_email: str = Field(max_length=255, unique=True)
    account_phone_number: str | None = Field(default=None, max_length=20, unique=True)
    account_hash_password: str | None = Field(default=None, max_length=255)
    account_google_sub: str | None = Field(default=None, max_length=255, unique=True)
    account_status: str | None = Field(default=None, max_length=20, sa_column_kwargs={"server_default": text("'ACTIVE'"), "nullable": False})
    account_name: str | None = Field(default=None, max_length=255)
    account_date_of_birth: date | None = None
    account_house_number: str | None = Field(default=None, max_length=255)
    account_ward: str | None = Field(default=None, max_length=100)
    account_city: str | None = Field(default=None, max_length=255)
    account_country: str | None = Field(default=None, max_length=100)
    account_created_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))


class IdentitySession(SQLModel, table=True):
    __tablename__ = "session"
    __table_args__ = {"schema": "identity"}

    session_key: UUID | None = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    session_account_key: UUID = Field(foreign_key="identity.account.account_key")
    session_token_hash: str = Field(max_length=64, unique=True)
    session_created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))
    session_last_seen_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))
    session_expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
