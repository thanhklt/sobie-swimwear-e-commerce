"""Schema đầu vào / đầu ra và enum trạng thái của module inventory."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

_MAX_INT4 = 2_147_483_647
_MAX_NUMERIC_12 = 999_999_999_999
_INT_LEXICAL_RE = re.compile(r"^[+-]?[0-9]+$")
_EMAIL_ADAPTER: TypeAdapter[EmailStr] = TypeAdapter(EmailStr)


def _strip_text(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    return value


def _validate_optional_email(value: str) -> str:
    if not value:
        return ""
    try:
        return str(_EMAIL_ADAPTER.validate_python(value))
    except ValidationError as exc:
        raise ValueError(exc.errors()[0]["msg"]) from exc


def _parse_strict_int(value: object) -> int:
    # Reject bool explicitly because bool is a subclass of int in Python.
    if isinstance(value, bool):
        raise ValueError("Value must be an integer, not a boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not _INT_LEXICAL_RE.fullmatch(stripped):
            raise ValueError("Value must be an integer string")
        return int(stripped)
    raise ValueError("Value must be an integer")


TrimmedRequiredName = Annotated[
    str,
    BeforeValidator(_strip_text),
    Field(min_length=1, max_length=255),
]
TrimmedRequiredPhone = Annotated[
    str,
    BeforeValidator(_strip_text),
    Field(min_length=1, max_length=20),
]
TrimmedOptionalEmail = Annotated[
    str,
    BeforeValidator(_strip_text),
    Field(max_length=255),
    AfterValidator(_validate_optional_email),
]
TrimmedOptionalAddress = Annotated[
    str,
    BeforeValidator(_strip_text),
    Field(max_length=255),
]
StrictPositiveInt4 = Annotated[
    int,
    BeforeValidator(_parse_strict_int),
    Field(ge=1, le=_MAX_INT4),
]
StrictNonNegativeVnd = Annotated[
    int,
    BeforeValidator(_parse_strict_int),
    Field(ge=0, le=_MAX_NUMERIC_12),
]


class SupplierStatus(StrEnum):
    """Trạng thái hợp tác của nhà cung cấp."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ReceiptStatus(StrEnum):
    """Trạng thái vòng đời phiếu nhập kho."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class SupplierInput(BaseModel):
    """Dữ liệu đầu vào khi tạo hoặc cập nhật nhà cung cấp (UC-32)."""

    name: TrimmedRequiredName
    phone_number: TrimmedRequiredPhone
    email: TrimmedOptionalEmail = ""
    address: TrimmedOptionalAddress = ""


class ReceiptLineInput(BaseModel):
    """Một dòng chi tiết biến thể trong phiếu nhập kho (UC-33)."""

    variant_key: UUID
    quantity: StrictPositiveInt4
    unit_price: StrictNonNegativeVnd

    @property
    def total_price(self) -> int:
        return self.quantity * self.unit_price

    @model_validator(mode="after")
    def _validate_line_total(self) -> ReceiptLineInput:
        if self.total_price > _MAX_NUMERIC_12:
            raise ValueError(f"Line total must be <= {_MAX_NUMERIC_12}")
        return self


class ReceiptInput(BaseModel):
    """Dữ liệu đầu vào khi lập hoặc sửa phiếu nhập kho nháp (UC-33)."""

    supplier_key: UUID
    lines: list[ReceiptLineInput] = Field(min_length=1)

    @property
    def total_price(self) -> int:
        return sum(line.total_price for line in self.lines)

    @field_validator("lines")
    @classmethod
    def _validate_lines(cls, lines: list[ReceiptLineInput]) -> list[ReceiptLineInput]:
        seen_variants: set[UUID] = set()
        for line in lines:
            if line.variant_key in seen_variants:
                raise ValueError("Duplicate variant_key in receipt lines")
            seen_variants.add(line.variant_key)
        if sum(line.total_price for line in lines) > _MAX_NUMERIC_12:
            raise ValueError(f"Receipt total must be <= {_MAX_NUMERIC_12}")
        return lines
