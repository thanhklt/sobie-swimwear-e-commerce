"""Nghiệp vụ UC-28/29/30/31; không phụ thuộc giao diện quản trị."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.modules.catalog import service as catalog_service
from app.modules.promotion import repository
from app.shared.database.transaction import transaction
from app.shared.money import discounted_price, percent_of

LOCAL_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def _as_utc(local_date: date, *, next_day: bool = False) -> datetime:
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
    kind = form["promotion_type"]
    if kind not in {"PRODUCT", "ORDER", "CODE"}:
        raise ValueError("Loại khuyến mãi không hợp lệ.")
    discount = Decimal(str(form["discount_percentage"]))
    if not Decimal("0") < discount < Decimal("100"):
        raise ValueError("Phần trăm giảm phải lớn hơn 0 và nhỏ hơn 100.")
    if discount != discount.quantize(Decimal("0.01")):
        raise ValueError("Phần trăm giảm chỉ được có tối đa 2 chữ số thập phân.")
    data: dict[str, Any] = {"promotion_type": kind, "discount_percentage": discount}
    if kind == "PRODUCT":
        product_id = (form.get("product_id") or "").strip().upper()
        if not product_id:
            raise ValueError("Vui lòng chọn sản phẩm.")
        if form.get("start_date") or form.get("end_date") or form.get("quantity"):
            raise ValueError("Khuyến mãi sản phẩm không có ngày hiệu lực hoặc giới hạn lượt.")
        data.update(product_id=product_id, quantity=None, start_date=None, end_date=None)
    else:
        threshold = form.get("threshold_price")
        quantity = form.get("quantity")
        start_date, end_date = form.get("start_date"), form.get("end_date")
        if threshold is None or int(threshold) < 0:
            raise ValueError("Giá trị đơn tối thiểu phải lớn hơn hoặc bằng 0.")
        if quantity is None or int(quantity) < 1:
            raise ValueError("Số lượng được áp dụng phải từ 1 trở lên.")
        if not start_date or not end_date or end_date <= start_date:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu.")
        data.update(threshold_price=int(threshold), quantity=int(quantity),
                    start_date=_as_utc(start_date), end_date=_as_utc(end_date, next_day=True))
        if kind == "CODE":
            code = (form.get("code") or "").strip()
            if not code:
                raise ValueError("Vui lòng nhập mã voucher.")
            if len(code) > 50:
                raise ValueError("Mã voucher dài tối đa 50 ký tự.")
            data["code"] = code
    async with transaction(db):
        # Same lock used for KM allocation, so duplicate product checks cannot race.
        await db.exec(text("SELECT pg_advisory_xact_lock(64213, 1)"))
        if kind == "PRODUCT":
            product_key = await catalog_service.active_product_key(db, data["product_id"])
            if product_key is None:
                raise ValueError("Không tìm thấy sản phẩm đang bán.")
            if await repository.product_has_active_promotion(db, product_key):
                raise ValueError(f"Sản phẩm {data['product_id']} đã thuộc một khuyến mãi chưa kết thúc.")
            data["product_key"] = product_key
        created = await repository.create_promotion(db, data)
    created["status"] = display_status({
        "promotion_status": "ENABLED", "promotion_start_date": data["start_date"],
        "promotion_end_date": data["end_date"], "promotion_used_amount": 0,
        "promotion_quantity": data["quantity"],
    })
    return created


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
    product_discount = sum((price - discounted_price(price, pct)) * quantity for price, quantity, pct in product_lines)
    orders = await repository.find_eligible_order_promotions(db, subtotal, now)
    best_order = max(orders, key=lambda r: percent_of(subtotal, Decimal(r["discount_percentage"])), default=None)
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
        elif subtotal < voucher["threshold_price"]:
            notice = f"Đơn hàng cần đạt tối thiểu {voucher['threshold_price']:,}đ để dùng voucher."
        else:
            voucher_amount = percent_of(subtotal, Decimal(voucher["discount_percentage"]))
            if voucher_amount >= amount:
                selected, source, amount = voucher, "CODE", voucher_amount
            else:
                notice = "Khuyến mãi theo hóa đơn giảm nhiều hơn; voucher không được áp dụng."
    return {"subtotal": subtotal, "product_discount": product_discount,
            "selected_discount": amount, "selected_source": source,
            "selected_promotion_id": selected["promotion_id"] if selected else None,
            "selected_promotion_key": selected["promotion_key"] if selected else None,
            "notice": notice}


async def consume_promotion(db, promotion_key) -> bool:
    """Gọi trong transaction tạo đơn; UPDATE giới hạn lượt một cách nguyên tử."""
    return await repository.increment_used(db, promotion_key)


async def refund_promotion(db, promotion_key) -> None:
    """Gọi trong transaction hủy đơn; giữ số lượt không âm."""
    await repository.decrement_used(db, promotion_key)
