"""DTO identity — API / service công khai."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ShippingAddressCreate:
    name: str
    phone: str
    house_number: str
    ward: str
    city: str
    country: str = "Việt Nam"


@dataclass(frozen=True, slots=True)
class ShippingAddressView:
    shipping_address_key: UUID
    account_key: UUID
    name: str
    phone: str
    house_number: str
    ward: str
    city: str
    country: str
    is_default: bool
