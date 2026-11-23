"""Kiểm tra tiêu chí UC-28..31, UC-36 và UC-40 ở tầng nghiệp vụ."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
import os

import pytest

from app.modules.ordering import service as ordering_service
from app.modules.promotion import service as promotion_service
from app.shared.money import discounted_price, percent_of


def test_uc28_ac10_round_half_up_product_price():
    assert discounted_price(199_999, Decimal("15")) == 169_999


def test_uc28_ac4_product_promotion_is_immediately_active():
    row = {"promotion_status": "ENABLED", "promotion_start_date": None,
           "promotion_end_date": None, "promotion_used_amount": 0,
           "promotion_quantity": None}
    assert promotion_service.display_status(row) == "Đang hiệu lực"


def test_uc28_ac1_product_price_uses_active_product_promotion(monkeypatch):
    async def product_key(_db, product_id):
        assert product_id == "SP-0001"
        return "product-key"
    async def promotion(_db, product_id):
        assert product_id == "product-key"
        return {"discount_percentage": Decimal("10"), "promotion_id": "KM-0001"}
    monkeypatch.setattr(promotion_service.catalog_service, "active_product_key", product_key)
    monkeypatch.setattr(promotion_service.repository, "product_promotion_for_product", promotion)
    assert asyncio.run(promotion_service.product_price(object(), "SP-0001", 300_000)) == (270_000, "KM-0001")


@pytest.mark.parametrize("form", [
    {"promotion_type": "PRODUCT", "discount_percentage": 0, "product_id": "SP-0001"},
    {"promotion_type": "PRODUCT", "discount_percentage": 120, "product_id": "SP-0001"},
    {"promotion_type": "PRODUCT", "discount_percentage": 10, "product_id": ""},
])
def test_uc28_ac5_invalid_product_promotion_is_rejected_before_save(form):
    with pytest.raises(ValueError):
        asyncio.run(promotion_service.create_promotion(object(), form))


def test_uc29_ac4_invalid_schedule_is_rejected_before_save():
    form = {"promotion_type": "ORDER", "discount_percentage": 10,
            "threshold_price": -1, "quantity": 0,
            "start_date": datetime(2026, 11, 25).date(),
            "end_date": datetime(2026, 11, 20).date()}
    with pytest.raises(ValueError):
        asyncio.run(promotion_service.create_promotion(object(), form))


def test_uc29_ac10_status_uses_enabled_and_time_window():
    now = datetime(2026, 11, 20, 12, tzinfo=UTC)
    upcoming = {"promotion_status": "ENABLED", "promotion_start_date": now + timedelta(days=5),
                "promotion_end_date": now + timedelta(days=10), "promotion_used_amount": 0,
                "promotion_quantity": 10}
    stopped = {**upcoming, "promotion_status": "DISABLED"}
    assert promotion_service.display_status(upcoming, now) == "Sắp diễn ra"
    assert promotion_service.display_status(stopped, now) == "Đã kết thúc"


def test_uc31_ac2_ac3_ac4_select_larger_discount_and_prefer_voucher_on_tie(monkeypatch):
    async def quote(order_percent, voucher_percent):
        async def eligible(db, subtotal, now):
            return [] if order_percent is None else [{
                "promotion_key": "order-key", "promotion_id": "KM-0001",
                "discount_percentage": Decimal(order_percent),
            }]

        async def voucher(db, code):
            if voucher_percent is None:
                return None
            now = datetime.now(UTC)
            return {"promotion_key": "code-key", "promotion_id": "KM-0002",
                    "promotion_status": "ENABLED", "promotion_used_amount": 0,
                    "promotion_quantity": 10, "promotion_start_date": now - timedelta(days=1),
                    "promotion_end_date": now + timedelta(days=1),
                    "threshold_price": 0, "discount_percentage": Decimal(voucher_percent)}

        monkeypatch.setattr(promotion_service.repository, "find_eligible_order_promotions", eligible)
        monkeypatch.setattr(promotion_service.repository, "find_code_promotion", voucher)
        return await promotion_service.quote_order_discount(object(), 500_000, voucher_code="SUMMER10")

    assert asyncio.run(quote("6", "10"))["selected_source"] == "CODE"
    assert asyncio.run(quote("10", "6"))["selected_source"] == "ORDER"
    assert asyncio.run(quote("8", "8"))["selected_source"] == "CODE"


def _patch_tx(monkeypatch, module):
    @asynccontextmanager
    async def passthrough(_db):
        yield _db
    monkeypatch.setattr(module, "transaction", passthrough)


def _shipping_order(status):
    return {"order_key": "order-key", "order_code": "7K3M9Q2X", "order_status": status,
            "order_payment_status": "UNPAID", "order_shipping_fee": 30_000,
            "order_total_price": 480_000, "order_discount_amount": 50_000,
            "order_customer_name": "Khách Demo", "order_customer_phone_number": "0900000000",
            "order_customer_house_number": "1 Đường A", "order_customer_ward": "Phường B",
            "order_customer_city": "TP.HCM", "order_customer_country": "Việt Nam",
            "order_account_key": "account-key", "order_payment_key": "payment-key",
            "payment_name": "COD"}


def test_uc36_ac2_public_simulator_data_contains_no_customer_pii(monkeypatch):
    async def rows(_db):
        return [{"order_code": "7K3M9Q2X", "order_status": "AWAITING_PICKUP"}]
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "shipping_orders", rows)
    result = asyncio.run(ordering_service.list_shipping_orders(object()))
    assert result == [{"order_code": "7K3M9Q2X", "status": "AWAITING_PICKUP", "status_label": "Chờ lấy hàng"}]


def test_uc36_ac1_ac2_shipping_website_renders_public_order_status(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.modules.shipping import router as shipping_router

    async def orders(_db):
        return [{"order_code": "7K3M9Q2X", "status": "AWAITING_PICKUP", "status_label": "Chờ lấy hàng"}]
    async def fake_db():
        yield object()

    monkeypatch.setattr(ordering_service, "list_shipping_orders", orders)
    app.dependency_overrides[shipping_router._db] = fake_db
    try:
        response = TestClient(app).get("/shipping/")
    finally:
        app.dependency_overrides.pop(shipping_router._db, None)
    assert response.status_code == 200
    assert "7K3M9Q2X" in response.text
    assert "Chờ lấy hàng" in response.text
    assert "0900000000" not in response.text
    assert "name=\"action\" value=\"received\"" in response.text


def test_uc28_29_30_ac2_admin_template_has_confirmation_and_no_edit(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.modules.promotion import router as promotion_router

    async def rows(_db, *_args):
        return []
    async def fake_db():
        yield object()

    monkeypatch.setattr(promotion_service, "list_promotions", rows)
    app.dependency_overrides[promotion_router.employee_only] = lambda: object()
    app.dependency_overrides[promotion_router._db] = fake_db
    try:
        response = TestClient(app).get("/admin/promotions")
    finally:
        app.dependency_overrides.pop(promotion_router.employee_only, None)
        app.dependency_overrides.pop(promotion_router._db, None)
    assert response.status_code == 200
    assert "Xác nhận tạo" in response.text
    assert "đã tạo thì không thể sửa" in response.text
    assert "Số lượt tối đa" in response.text
    assert "Sửa chương trình" not in response.text


def test_uc36_ac3_received_order_changes_to_shipping(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "shipping_order_for_update",
                        lambda *_args: asyncio.sleep(0, result=_shipping_order("AWAITING_PICKUP")))
    monkeypatch.setattr(ordering_service.repository, "order_lines_for_delivery",
                        lambda *_args: asyncio.sleep(0, result=[]))
    changed = []
    async def update(*args):
        changed.append(args[2:])
    monkeypatch.setattr(ordering_service.repository, "update_shipping_status", update)
    assert asyncio.run(ordering_service.update_shipping_status(object(), "7k3m9q2x", "received")) == "Đang giao"
    assert changed == [("AWAITING_PICKUP", "SHIPPING")]


def test_uc36_ac4_delivery_creates_invoice_and_sets_cod_paid(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "shipping_order_for_update",
                        lambda *_args: asyncio.sleep(0, result=_shipping_order("SHIPPING")))
    monkeypatch.setattr(ordering_service.repository, "order_lines_for_delivery",
                        lambda *_args: asyncio.sleep(0, result=[]))
    monkeypatch.setattr(ordering_service.catalog_service, "invoice_variant_details",
                        lambda *_args: asyncio.sleep(0, result={}))
    monkeypatch.setattr(ordering_service.identity_service, "account_email",
                        lambda *_args: asyncio.sleep(0, result="guest@example.test"))
    invoices, changed = [], []
    async def save_invoice(_db, order, snapshot):
        invoices.append((order["order_code"], snapshot["total_payment"], snapshot["payment_method"], snapshot["customer"]["email"]))
    async def update(*args): changed.append(args[2:])
    monkeypatch.setattr(ordering_service.repository, "create_delivery_invoice", save_invoice)
    monkeypatch.setattr(ordering_service.repository, "update_shipping_status", update)
    asyncio.run(ordering_service.update_shipping_status(object(), "7K3M9Q2X", "delivered"))
    assert invoices == [("7K3M9Q2X", 480_000, "COD", "guest@example.test")]
    assert changed == [("SHIPPING", "DELIVERED")]


def test_uc36_ac5_failed_delivery_restocks_once(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "shipping_order_for_update",
                        lambda *_args: asyncio.sleep(0, result=_shipping_order("SHIPPING")))
    lines = [{"order_detail_variant_key": "variant-key", "order_detail_quantity": 2}]
    monkeypatch.setattr(ordering_service.repository, "order_lines_for_delivery",
                        lambda *_args: asyncio.sleep(0, result=lines))
    restocked, changed = [], []
    async def restore(_db, rows): restocked.extend(rows)
    async def update(*args): changed.append(args[2:])
    monkeypatch.setattr(ordering_service.inventory_service, "restore_failed_delivery_stock", restore)
    monkeypatch.setattr(ordering_service.repository, "update_shipping_status", update)
    asyncio.run(ordering_service.update_shipping_status(object(), "7K3M9Q2X", "failed"))
    assert restocked == [("variant-key", 2)]
    assert changed == [("SHIPPING", "DELIVERY_FAILED")]


def test_uc36_ac6_stale_order_status_is_rejected(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "shipping_order_for_update",
                        lambda *_args: asyncio.sleep(0, result=_shipping_order("DELIVERED")))
    with pytest.raises(ValueError, match="không thể thực hiện"):
        asyncio.run(ordering_service.update_shipping_status(object(), "7K3M9Q2X", "failed"))


def test_uc40_ac1_handoff_writes_only_confirmed_order(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    calls = []
    async def handoff(_db, code, employee_key):
        calls.append((code, employee_key))
        return "order-key"
    monkeypatch.setattr(ordering_service.repository, "handoff_order", handoff)
    assert asyncio.run(ordering_service.handoff_order(object(), "7k3m9q2x", "employee-key"))
    assert calls == [("7K3M9Q2X", "employee-key")]


def test_promotion_sql_uses_existing_schema_when_database_is_configured():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("Set DATABASE_URL to run the PostgreSQL integration check.")

    async def check():
        from app.modules.promotion import repository
        from app.modules.catalog import repository as catalog_repository
        from app.shared.database.engine import engine, session_factory

        class RollbackCheck(Exception):
            pass

        async with session_factory() as db:
            try:
                async with db.begin():
                    now = datetime.now(UTC)
                    product = await repository.create_promotion(db, {
                        "promotion_type": "PRODUCT", "discount_percentage": Decimal("10"),
                        "product_key": (await catalog_repository.active_product_key(db, "SP-0002")), "quantity": None,
                        "start_date": None, "end_date": None,
                    })
                    order = await repository.create_promotion(db, {
                        "promotion_type": "ORDER", "discount_percentage": Decimal("8"),
                        "threshold_price": 0, "quantity": 3,
                        "start_date": now - timedelta(days=1), "end_date": now + timedelta(days=1),
                    })
                    voucher = await repository.create_promotion(db, {
                        "promotion_type": "CODE", "discount_percentage": Decimal("9"),
                        "threshold_price": 0, "quantity": 3,
                        "start_date": now - timedelta(days=1), "end_date": now + timedelta(days=1),
                        "code": "UC30-SMOKE",
                    })
                    rows = await repository.list_promotions(db)
                    assert {row["promotion_type"] for row in rows} >= {"PRODUCT", "ORDER", "CODE"}
                    assert await repository.product_has_active_promotion(db, product["product_key"])
                    assert await repository.find_code_promotion(db, "uc30-smoke") is not None
                    eligible = await repository.find_eligible_order_promotions(db, 100_000, now)
                    assert any(row["promotion_key"] == order["promotion_key"] for row in eligible)
                    assert product["promotion_id"].startswith("KM-")
                    assert voucher["promotion_id"].startswith("KM-")
                    raise RollbackCheck
            except RollbackCheck:
                pass
        await engine.dispose()

    asyncio.run(check())
