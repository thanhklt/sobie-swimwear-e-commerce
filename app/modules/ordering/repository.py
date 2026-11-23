"""Truy vấn các bảng thuộc schema ordering."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text


async def shipping_orders(db) -> list[dict[str, Any]]:
    result = await db.exec(text('''
        SELECT order_code, order_status
        FROM ordering."order"
        WHERE order_status IN ('AWAITING_PICKUP', 'SHIPPING')
        ORDER BY order_created_date
    '''))
    return [dict(row) for row in result.mappings().all()]


async def shipping_order_for_update(db, order_code: str):
    result = await db.exec(text('''
        SELECT order_key, order_code, order_status, order_payment_status,
               order_shipping_fee, order_total_price, order_discount_amount,
               order_customer_name, order_customer_phone_number,
               order_customer_house_number, order_customer_ward,
               order_customer_city, order_customer_country,
               order_account_key, order_payment_key, payment.payment_name
        FROM ordering."order" AS order_row
        JOIN ordering.payment AS payment ON payment.payment_key = order_row.order_payment_key
        WHERE order_code = :order_code FOR UPDATE OF order_row
    '''), params={"order_code": order_code})
    row = result.mappings().one_or_none()
    return dict(row) if row else None


async def update_shipping_status(db, order_key, old_status: str, new_status: str) -> None:
    await db.exec(text('''
        UPDATE ordering."order"
        SET order_status = :new_status, order_updated_date = now()
        WHERE order_key = :order_key AND order_status = :old_status
    '''), params={"order_key": order_key, "old_status": old_status, "new_status": new_status})
    await db.exec(text('''
        INSERT INTO ordering.order_status_history
            (order_status_history_order_key, order_status_history_from_value,
             order_status_history_to_value, order_status_history_source)
        VALUES (:order_key, :old_status, :new_status, 'SHIPPING_SIMULATOR')
    '''), params={"order_key": order_key, "old_status": old_status, "new_status": new_status})


async def order_lines_for_delivery(db, order_key) -> list[dict[str, Any]]:
    result = await db.exec(text('''
        SELECT order_detail_variant_key, order_detail_quantity, order_detail_unit_price,
               order_detail_product_promotion_key
        FROM ordering.order_detail WHERE order_detail_order_key = :order_key
    '''), params={"order_key": order_key})
    return [dict(row) for row in result.mappings().all()]


async def create_delivery_invoice(db, order: dict[str, Any], snapshot: dict[str, Any]) -> None:
    await db.exec(text('''
        UPDATE ordering."order" AS order_row SET order_payment_status = 'PAID'
        WHERE order_key = :order_key AND EXISTS (
            SELECT 1 FROM ordering.payment
            WHERE payment_key = order_row.order_payment_key AND payment_name = :payment_name
        )
    '''), params={"order_key": order["order_key"], "payment_name": order["payment_name"]})
    await db.exec(text('''
        INSERT INTO ordering.invoice (invoice_id, invoice_order_key, invoice_snapshot_json)
        VALUES (:invoice_id, :order_key, CAST(:snapshot AS jsonb))
        ON CONFLICT (invoice_order_key) DO NOTHING
    '''), params={"invoice_id": f"HD-{order['order_code']}", "order_key": order["order_key"], "payment_name": "COD", "snapshot": json.dumps(snapshot, ensure_ascii=False, default=str)})


async def handoff_order(db, order_code: str, employee_key) -> str | None:
    result = await db.exec(text('''
        UPDATE ordering."order"
        SET order_status = 'AWAITING_PICKUP', order_updated_date = now()
        WHERE order_code = :order_code AND order_status = 'CONFIRMED'
        RETURNING order_key
    '''), params={"order_code": order_code})
    row = result.mappings().one_or_none()
    if row is None:
        return None
    await db.exec(text('''
        INSERT INTO ordering.order_status_history
            (order_status_history_order_key, order_status_history_from_value,
             order_status_history_to_value, order_status_history_source,
             order_status_history_changed_by_key)
        VALUES (:order_key, 'CONFIRMED', 'AWAITING_PICKUP', 'EMPLOYEE', :employee_key)
    '''), params={"order_key": row["order_key"], "employee_key": employee_key})
    return str(row["order_key"])


async def confirmed_orders(db) -> list[dict[str, Any]]:
    result = await db.exec(text('''
        SELECT order_code, order_created_date FROM ordering."order"
        WHERE order_status = 'CONFIRMED' ORDER BY order_created_date
    '''))
    return [dict(row) for row in result.mappings().all()]
