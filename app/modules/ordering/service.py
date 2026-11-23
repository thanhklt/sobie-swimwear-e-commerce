"""Các nghiệp vụ vòng đời đơn công khai cho shipping."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.modules.catalog import service as catalog_service
from app.modules.inventory import service as inventory_service
from app.modules.identity import service as identity_service
from app.modules.ordering import repository
from app.modules.promotion import service as promotion_service
from app.shared.database.transaction import transaction
from app.shared.money import discounted_price

ORDER_STATUS_LABELS = {
    "PENDING": "Chưa xử lý", "CONFIRMED": "Đã xác nhận",
    "AWAITING_PICKUP": "Chờ lấy hàng", "SHIPPING": "Đang giao",
    "DELIVERED": "Giao thành công", "DELIVERY_FAILED": "Giao không thành công",
    "CANCELLED": "Đã hủy",
}


async def list_shipping_orders(db):
    async with transaction(db):
        rows = await repository.shipping_orders(db)
    return [{"order_code": row["order_code"], "status": row["order_status"],
             "status_label": ORDER_STATUS_LABELS[row["order_status"]]} for row in rows]


async def update_shipping_status(db, order_code: str, action: str) -> str:
    transitions = {
        "received": ("AWAITING_PICKUP", "SHIPPING"),
        "delivered": ("SHIPPING", "DELIVERED"),
        "failed": ("SHIPPING", "DELIVERY_FAILED"),
    }
    if action not in transitions:
        raise ValueError("Thao tác giao hàng không hợp lệ.")
    old_status, new_status = transitions[action]
    async with transaction(db):
        order = await repository.shipping_order_for_update(db, order_code.strip().upper())
        if order is None:
            raise LookupError("Không tìm thấy đơn hàng.")
        if order["order_status"] != old_status:
            raise ValueError(f"Đơn đang ở trạng thái {ORDER_STATUS_LABELS[order['order_status']]}; không thể thực hiện thao tác này.")
        lines = await repository.order_lines_for_delivery(db, order["order_key"])
        if new_status == "DELIVERY_FAILED":
            await inventory_service.restore_failed_delivery_stock(
                db, [(line["order_detail_variant_key"], line["order_detail_quantity"]) for line in lines]
            )
        if new_status == "DELIVERED":
            variants = await catalog_service.invoice_variant_details(
                db, [line["order_detail_variant_key"] for line in lines]
            )
            items = []
            product_discount = 0
            subtotal = 0
            for line in lines:
                variant = variants.get(line["order_detail_variant_key"], {})
                original = int(line["order_detail_unit_price"])
                quantity = line["order_detail_quantity"]
                promo_key = line["order_detail_product_promotion_key"]
                percentage = await promotion_service.product_promotion_discount(db, promo_key) if promo_key else None
                sale_price = discounted_price(original, percentage) if percentage is not None else original
                line_discount = (original - sale_price) * quantity
                subtotal += original * quantity
                product_discount += line_discount
                items.append({
                    "product_name": variant.get("product_name", "Sản phẩm"),
                    "variant_id": variant.get("variant_id"),
                    "color": variant.get("color_name"), "size": variant.get("size_name"),
                    "unit_price": original, "discounted_unit_price": sale_price,
                    "quantity": quantity, "discount_amount": line_discount,
                })
            snapshot = {
                "order_code": order["order_code"], "created_at": datetime.now(UTC).isoformat(),
                "items": items, "subtotal": subtotal,
                "product_discount": product_discount,
                "order_discount": int(order["order_discount_amount"]),
                "shipping_fee": int(order["order_shipping_fee"]),
                "total_payment": int(order["order_total_price"]),
                "customer": {
                    "name": order["order_customer_name"], "phone": order["order_customer_phone_number"],
                    "address": ", ".join(filter(None, [order["order_customer_house_number"],
                        order["order_customer_ward"], order["order_customer_city"], order["order_customer_country"]])),
                    "email": await identity_service.account_email(db, order["order_account_key"]),
                }, "payment_method": order["payment_name"],
            }
            await repository.create_delivery_invoice(db, order, snapshot)
        await repository.update_shipping_status(db, order["order_key"], old_status, new_status)
    return ORDER_STATUS_LABELS[new_status]


async def handoff_order(db, order_code: str, employee_key) -> bool:
    async with transaction(db):
        return await repository.handoff_order(db, order_code.strip().upper(), employee_key) is not None


async def list_confirmed_orders(db):
    async with transaction(db):
        rows = await repository.confirmed_orders(db)
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    return [{**row, "order_created_date": row["order_created_date"].astimezone(tz)} for row in rows]
