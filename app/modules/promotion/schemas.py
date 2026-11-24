"""DTO cho các UC khuyến mãi; không làm thay đổi cấu trúc database."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


PromotionType = Literal["PRODUCT", "ORDER", "CODE"]


class PromotionCreate(BaseModel):
    promotion_type: PromotionType
    discount_percentage: Decimal = Field(gt=0, lt=100, max_digits=5, decimal_places=2)
    product_id: str | None = None
    threshold_price: int | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, gt=0)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


class PromotionView(BaseModel):
    promotion_id: str
    promotion_type: PromotionType
    status: Literal["Sắp diễn ra", "Đang hiệu lực", "Đã kết thúc"]
    discount_percentage: Decimal
    product_id: str | None = None
    code: str | None = None
    threshold_price: int | None = None
    quantity: int | None = None
    used_amount: int
    start_date: datetime | None = None
    end_date: datetime | None = None


class DiscountQuote(BaseModel):
    subtotal: int
    product_discount: int
    selected_discount: int
    selected_source: Literal["ORDER", "CODE", "NONE"]
    selected_promotion_id: str | None = None
    notice: str | None = None
