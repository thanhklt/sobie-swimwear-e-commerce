"""Shipping request and public response schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ShippingStatus = Literal["AWAITING_PICKUP", "SHIPPING"]
ShippingAction = Literal["received", "delivered", "failed"]


class ShippingActionRequest(BaseModel):
    action: ShippingAction


class ShippingOrderView(BaseModel):
    """The public simulator deliberately excludes customer and payment data."""

    model_config = ConfigDict(extra="ignore")

    order_code: str = Field(pattern=r"^[0-9A-HJKMNP-TV-Z]{8}$")
    status: ShippingStatus
    status_label: str
