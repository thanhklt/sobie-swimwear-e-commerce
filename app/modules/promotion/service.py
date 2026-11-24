"""Nghiệp vụ UC-28/29/30/31; không phụ thuộc giao diện quản trị."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.modules.catalog import service as catalog_service
from app.modules.promotion import repository
from app.shared.database.transaction import transaction
from app.shared.money import discounted_price, percent_of

LOCAL_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


class PromotionValidationError(ValueError):
    """A field-specific validation error safe to show beside an input."""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field


def _as_utc(local_date: date, *, next_day: bool = False) -> datetime:
    """Convert a calendar date in Asia/Ho_Chi_Minh to a UTC timestamptz bound.

    Start date → 00:00:00 that day (inclusive).
    End date → 00:00:00 of the *next* day (exclusive), so the promotion applies
    through the end of the selected calendar day (UC-29/UC-30, BR-004).
    """
    value = local_date + timedelta(days=1) if next_day else local_date
    return datetime.combine(value, time.min, LOCAL_TZ).astimezone(UTC)


def display_status(row: dict[str, Any], now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    if row["promotion_status"] == "DISABLED":
        return "Đã kết thúc"
    start, end = row.get("promotion_start_date"), row.get("promotion_end_date")
    if start is None:
        return "Đang hiệu lực"
    if now < start:
        return "Sắp diễn ra"
    if now >= end:
        return "Đã kết thúc"
    return "Đang hiệu lực"


async def list_promotions(db, promotion_type: str | None = None, now: datetime | None = None):
    now = now or datetime.now(UTC)
    async with transaction(db):
        rows = await repository.list_promotions(db, promotion_type)
        product_keys = [r["product_key"] for r in rows if r.get("product_key")]
        product_ids = await catalog_service.product_ids_by_keys(db, product_keys)
    return [{
        "promotion_id": r["promotion_id"],
        "promotion_type": r["promotion_type"],
        "status": display_status(r, now),
        "discount_percentage": Decimal(r["discount_percentage"]),
        "product_id": product_ids.get(r.get("product_key")), "code": r.get("code"),
        "threshold_price": int(r["threshold_price"]) if r.get("threshold_price") is not None else None,
        "quantity": r.get("promotion_quantity"), "used_amount": r["promotion_used_amount"],
        "start_date": r["promotion_start_date"].astimezone(LOCAL_TZ) if r.get("promotion_start_date") else None,
        "end_date": r["promotion_end_date"].astimezone(LOCAL_TZ) - timedelta(days=1) if r.get("promotion_end_date") else None,
    } for r in rows]


async def create_promotion(db, form: dict[str, Any]):
    data = _normalise_promotion_form(form)
    kind = data["promotion_type"]
    async with transaction(db):
        # Serialize product membership checks and promotion-code allocation.
        await db.exec(text("SELECT pg_advisory_xact_lock(64213, 1)"))
        await _validate_promotion_references(db, data)
        created = await repository.create_promotion(db, data)
    created["status"] = display_status({
        "promotion_status": "ENABLED", "promotion_start_date": data["start_date"],
        "promotion_end_date": data["end_date"], "promotion_used_amount": 0,
        "promotion_quantity": data["quantity"],
    })
    return created


def _normalise_promotion_form(form: dict[str, Any]) -> dict[str, Any]:
    kind = str(form.get("promotion_type") or "").strip().upper()
    if kind not in {"PRODUCT", "ORDER", "CODE"}:
        raise PromotionValidationError("promotion_type", "Loại khuyến mãi không hợp lệ.")
    try:
        discount = Decimal(str(form.get("discount_percentage", "")))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PromotionValidationError("discount_percentage", "Vui lòng nhập phần trăm giảm hợp lệ.") from exc
    if not discount.is_finite() or not Decimal("0") < discount < Decimal("100"):
        raise PromotionValidationError("discount_percentage", "Phần trăm giảm phải lớn hơn 0 và nhỏ hơn 100.")
    try:
        rounded_discount = discount.quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise PromotionValidationError("discount_percentage", "Phần trăm giảm không hợp lệ.") from exc
    if discount != rounded_discount:
        raise PromotionValidationError("discount_percentage", "Phần trăm giảm chỉ được có tối đa 2 chữ số thập phân.")
    data: dict[str, Any] = {"promotion_type": kind, "discount_percentage": discount}
    if kind == "PRODUCT":
        product_id = (form.get("product_id") or "").strip().upper()
        if not product_id:
            raise PromotionValidationError("product_id", "Vui lòng chọn sản phẩm.")
        extra_fields = ("threshold_price", "quantity", "start_date", "end_date", "code")
        if any(form.get(field) not in (None, "") for field in extra_fields):
            raise PromotionValidationError(
                "product_id", "Khuyến mãi sản phẩm không có ngưỡng, ngày hiệu lực, mã hoặc giới hạn lượt."
            )
        data.update(product_id=product_id, quantity=None, start_date=None, end_date=None)
    else:
        threshold = form.get("threshold_price")
        quantity = form.get("quantity")
        try:
            threshold = int(threshold)
        except (TypeError, ValueError) as exc:
            raise PromotionValidationError("threshold_price", "Vui lòng nhập giá trị đơn tối thiểu hợp lệ.") from exc
        if threshold < 0:
            raise PromotionValidationError("threshold_price", "Giá trị đơn tối thiểu phải lớn hơn hoặc bằng 0.")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError) as exc:
            raise PromotionValidationError("quantity", "Số lượng được áp dụng phải từ 1 trở lên.") from exc
        if quantity < 1:
            raise PromotionValidationError("quantity", "Số lượng được áp dụng phải từ 1 trở lên.")
        start_date = _local_date(form.get("start_date"), "start_date")
        end_date = _local_date(form.get("end_date"), "end_date")
        if end_date <= start_date:
            raise PromotionValidationError("end_date", "Ngày kết thúc phải sau ngày bắt đầu.")
        data.update(threshold_price=int(threshold), quantity=int(quantity),
                    start_date=_as_utc(start_date), end_date=_as_utc(end_date, next_day=True))
        if kind == "CODE":
            code = (form.get("code") or "").strip()
            if not code:
                raise PromotionValidationError("code", "Vui lòng nhập mã voucher.")
            if len(code) > 50:
                raise PromotionValidationError("code", "Mã voucher dài tối đa 50 ký tự.")
            data["code"] = code
    return data


def _local_date(value: Any, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value or ""))
    except (TypeError, ValueError) as exc:
        label = "Ngày bắt đầu" if field == "start_date" else "Ngày kết thúc"
        raise PromotionValidationError(field, f"{label} chưa hợp lệ.") from exc


async def _validate_promotion_references(db, data: dict[str, Any]) -> None:
    if data["promotion_type"] == "PRODUCT":
        product_key = await catalog_service.active_product_key(db, data["product_id"])
        if product_key is None:
            raise PromotionValidationError("product_id", "Không tìm thấy sản phẩm đang bán.")
        if await repository.product_has_active_promotion(db, product_key):
            raise PromotionValidationError(
                "product_id", f"Sản phẩm {data['product_id']} đã thuộc một khuyến mãi chưa kết thúc."
            )
        data["product_key"] = product_key
    elif data["promotion_type"] == "CODE" and await repository.code_promotion_exists(db, data["code"]):
        raise PromotionValidationError("code", "Mã voucher đã tồn tại (không phân biệt hoa thường).")


async def validate_promotion(db, form: dict[str, Any]) -> dict[str, Any]:
    """Validate fields and database references before showing confirmation."""
    data = _normalise_promotion_form(form)
    async with transaction(db):
        await _validate_promotion_references(db, data)
    return data


async def end_promotion(db, promotion_id: str) -> bool:
    async with transaction(db):
        return await repository.end_promotion(db, promotion_id.strip().upper())


async def product_price(db, product_id: str, sell_price: int) -> tuple[int, str | None]:
    product_key = await catalog_service.active_product_key(db, product_id)
    if product_key is None:
        return sell_price, None
    promotion = await repository.product_promotion_for_product(db, product_key)
    if promotion is None:
        return sell_price, None
    return discounted_price(sell_price, Decimal(promotion["discount_percentage"])), promotion["promotion_id"]


async def product_promotion_discount(db, promotion_key) -> Decimal | None:
    """Thông tin dùng để tính đơn giá sau giảm trong snapshot hóa đơn."""
    return await repository.product_promotion_discount(db, promotion_key)


async def quote_order_discount(
    db, subtotal: int, *, voucher_code: str | None = None,
    product_lines: Iterable[tuple[int, int, Decimal]] = (), now: datetime | None = None,
) -> dict[str, Any]:
    """UC-31: subtotal đầu vào đã cộng giá sau khuyến mãi sản phẩm.

    product_lines gồm (giá gốc, số lượng, phần trăm giảm) để trả tổng tiền giảm sản phẩm.
    Gọi từ ordering trong transaction cùng tạo đơn và tăng lượt.
    """
    now = now or datetime.now(UTC)
    product_discount = sum(
        (price - discounted_price(price, pct)) * quantity for price, quantity, pct in product_lines
    )
    # Read-only: caller may already hold a transaction (checkout); do not open a nested one.
    orders = await repository.find_eligible_order_promotions(db, subtotal, now)
    best_order = max(
        orders,
        key=lambda r: percent_of(subtotal, Decimal(r["discount_percentage"])),
        default=None,
    )
    selected = None
    source = "NONE"
    amount = 0
    notice = None
    if best_order:
        amount = percent_of(subtotal, Decimal(best_order["discount_percentage"]))
        selected, source = best_order, "ORDER"
    if voucher_code:
        voucher = await repository.find_code_promotion(db, voucher_code)
        if voucher is None or voucher["promotion_status"] == "DISABLED":
            notice = "Voucher không hợp lệ."
        elif now < voucher["promotion_start_date"]:
            notice = "Voucher chưa đến thời gian hiệu lực."
        elif now >= voucher["promotion_end_date"]:
            notice = "Voucher đã hết hạn."
        elif voucher["promotion_used_amount"] >= voucher["promotion_quantity"]:
            notice = "Voucher đã hết lượt sử dụng."
        elif subtotal < int(voucher["threshold_price"]):
            notice = (
                f"Đơn hàng cần đạt tối thiểu {int(voucher['threshold_price']):,}đ để dùng voucher."
            )
        else:
            voucher_amount = percent_of(subtotal, Decimal(voucher["discount_percentage"]))
            if voucher_amount >= amount:
                selected, source, amount = voucher, "CODE", voucher_amount
            else:
                notice = "Khuyến mãi theo hóa đơn giảm nhiều hơn; voucher không được áp dụng."
    return {
        "subtotal": subtotal,
        "product_discount": int(product_discount),
        "selected_discount": int(amount),
        "selected_source": source,
        "selected_promotion_id": selected["promotion_id"] if selected else None,
        "selected_promotion_label": (
            f"Voucher {selected.get('code') or voucher_code}"
            if selected and source == "CODE"
            else f"Khuyến mãi hóa đơn {selected['promotion_id']}"
            if selected
            else "Không có ưu đãi đơn hàng"
        ),
        "selected_promotion_key": selected["promotion_key"] if selected else None,
        "notice": notice,
    }


async def consume_promotion(db, promotion_key) -> bool:
    """Gọi trong transaction tạo đơn; UPDATE giới hạn lượt một cách nguyên tử."""
    return await repository.increment_used(db, promotion_key)


async def refund_promotion(db, promotion_key) -> None:
    """Gọi trong transaction hủy đơn (UC-22/UC-24); hoàn cả voucher lẫn ORDER."""
    await repository.decrement_used(db, promotion_key)


def quote_requires_reconfirm(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    """UC-31 E5/AC-10: reconfirm when discount amount *or* source changes."""
    return (
        int(previous.get("selected_discount") or 0) != int(current.get("selected_discount") or 0)
        or (previous.get("selected_source") or "NONE") != (current.get("selected_source") or "NONE")
    )


async def confirm_order_discount(
    db, subtotal: int, *, voucher_code: str | None = None,
    previous_quote: dict[str, Any] | None = None,
    product_lines: Iterable[tuple[int, int, Decimal]] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    """Re-quote at checkout; if quote changed vs previous display, do not consume.

    Ordering phải gọi hàm này trong cùng transaction với tạo đơn, rồi
    `consume_promotion` khi `requires_reconfirm` là False và có `selected_promotion_key`.
    """
    quote = await quote_order_discount(
        db, subtotal, voucher_code=voucher_code, product_lines=product_lines, now=now,
    )
    if previous_quote is not None and quote_requires_reconfirm(previous_quote, quote):
        quote["requires_reconfirm"] = True
        if quote.get("notice") is None and (
            (previous_quote.get("selected_source") or "NONE") != quote["selected_source"]
        ):
            quote["notice"] = (
                "Nguồn mức giảm đã thay đổi; vui lòng xác nhận lại trước khi đặt hàng."
            )
        return quote
    quote["requires_reconfirm"] = False
    return quote
