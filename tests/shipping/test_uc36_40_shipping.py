"""Kiểm tra tiêu chí UC-36 và UC-40 ở tầng nghiệp vụ."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from app.modules.ordering import service as ordering_service


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
    from app.shipping_main import app
    from app.modules.shipping import public_router as shipping_router

    async def orders(_db):
        return [{"order_code": "7K3M9Q2X", "status": "AWAITING_PICKUP", "status_label": "Chờ lấy hàng"}]
    async def fake_db():
        yield object()

    monkeypatch.setattr(ordering_service, "list_shipping_orders", orders)
    app.dependency_overrides[shipping_router._db] = fake_db
    try:
        response = TestClient(app).get("/")
    finally:
        app.dependency_overrides.pop(shipping_router._db, None)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "7K3M9Q2X" in response.text
    assert "Chờ lấy hàng" in response.text
    assert "0900000000" not in response.text
    assert "name=\"action\" value=\"received\"" in response.text
    assert 'action="/orders/7K3M9Q2X/status"' in response.text


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


def test_uc40_e1_reports_actual_status_when_already_awaiting_pickup(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "handoff_order",
                        lambda *_a, **_k: asyncio.sleep(0, result=None))
    monkeypatch.setattr(ordering_service.repository, "order_status_by_code",
                        lambda *_a, **_k: asyncio.sleep(0, result="AWAITING_PICKUP"))
    with pytest.raises(ValueError, match="Chờ lấy hàng") as err:
        asyncio.run(ordering_service.handoff_order(object(), "7K3M9Q2X", "employee-key"))
    assert "Không tìm thấy" not in str(err.value)


def test_uc40_e2_reports_not_found_distinct_from_e1(monkeypatch):
    _patch_tx(monkeypatch, ordering_service)
    monkeypatch.setattr(ordering_service.repository, "handoff_order",
                        lambda *_a, **_k: asyncio.sleep(0, result=None))
    monkeypatch.setattr(ordering_service.repository, "order_status_by_code",
                        lambda *_a, **_k: asyncio.sleep(0, result=None))
    with pytest.raises(LookupError, match="Không tìm thấy đơn"):
        asyncio.run(ordering_service.handoff_order(object(), "ZZZZZZZZ", "employee-key"))


def test_uc36_search_filters_by_code_fragment_and_status(monkeypatch):
    from app.modules.shipping import service as shipping_service

    async def orders(_db):
        return [
            {"order_code": "7K3M9Q2X", "status": "AWAITING_PICKUP", "status_label": "Chờ lấy hàng"},
            {"order_code": "4HZP8W1N", "status": "SHIPPING", "status_label": "Đang giao"},
        ]
    monkeypatch.setattr(ordering_service, "list_shipping_orders", orders)
    filtered = asyncio.run(shipping_service.list_simulator_orders(object(), q="7K3M", status="AWAITING_PICKUP"))
    assert [row["order_code"] for row in filtered] == ["7K3M9Q2X"]


def test_shipping_site_is_separate_from_admin_app(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app as admin_app
    from app.shipping_main import app as shipping_app
    from app.modules.shipping import public_router

    async def orders(_db, **_kwargs):
        return []
    async def fake_db():
        yield object()

    monkeypatch.setattr(public_router.service, "list_simulator_orders", orders)
    shipping_app.dependency_overrides[public_router._db] = fake_db
    try:
        public_response = TestClient(shipping_app).get("/")
        admin_response = TestClient(admin_app).get("/shipping/")
    finally:
        shipping_app.dependency_overrides.pop(public_router._db, None)
    assert public_response.status_code == 200
    assert public_response.headers["cache-control"] == "no-store"
    assert admin_response.status_code == 404


def test_admin_shipping_page_is_not_cached(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.modules.shipping import router as shipping_router

    async def orders(_db, **_kwargs):
        return []
    async def fake_db():
        yield object()

    monkeypatch.setattr(shipping_router.service, "list_orders_ready_for_handoff", orders)
    app.dependency_overrides[shipping_router.employee_only] = lambda: object()
    app.dependency_overrides[shipping_router._db] = fake_db
    try:
        response = TestClient(app).get("/admin/shipping")
    finally:
        app.dependency_overrides.pop(shipping_router.employee_only, None)
        app.dependency_overrides.pop(shipping_router._db, None)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_delivery_invoice_sql_marks_only_cod_orders_paid(monkeypatch):
    from app.modules.ordering import repository

    statements = []

    class FakeDb:
        async def exec(self, statement, params):
            statements.append((str(statement), params))

    asyncio.run(repository.create_delivery_invoice(
        FakeDb(), {"order_key": "qr-order", "order_code": "7K3M9Q2X", "payment_name": "QR"}, {},
    ))
    update_sql, params = statements[0]
    assert params["payment_name"] == "QR"
    assert "AND :payment_name = 'COD'" in update_sql
    assert "AND EXISTS" in update_sql
    assert "payment_name = :payment_name" in update_sql


def test_delivery_invoice_cod_guard_in_postgresql():
    import os
    from sqlalchemy import text

    if not os.environ.get("DATABASE_URL"):
        pytest.skip("Set DATABASE_URL to run the PostgreSQL integration check.")

    async def check():
        from app.modules.ordering import repository
        from app.shared.database.engine import engine, session_factory

        class RollbackCheck(Exception):
            pass

        async with session_factory() as db:
            try:
                async with db.begin():
                    rows = (await db.exec(text('''
                        SELECT o.order_key, o.order_code, o.order_payment_key, p.payment_name
                        FROM ordering."order" o
                        JOIN ordering.payment p ON p.payment_key = o.order_payment_key
                        WHERE o.order_code IN ('B6TQ2R5D', 'D5W9H2K7')
                    '''))).mappings().all()
                    if len(rows) < 2:
                        pytest.skip("The PostgreSQL seed must include two demo orders.")
                    qr_payment = (await db.exec(text('''
                        SELECT payment_key FROM ordering.payment WHERE payment_name = 'QR'
                    '''))).mappings().one()
                    cod = next(row for row in rows if row["payment_name"] == "COD")
                    qr = next(row for row in rows if row["order_key"] != cod["order_key"])
                    qr = dict(qr)
                    qr["payment_name"] = "QR"
                    await db.exec(text('''
                        UPDATE ordering."order"
                        SET order_payment_key = :qr_payment_key, order_payment_status = 'UNPAID'
                        WHERE order_key = :qr_key
                    '''), params={"qr_payment_key": qr_payment["payment_key"], "qr_key": qr["order_key"]})
                    await db.exec(text('''
                        UPDATE ordering."order" SET order_payment_status = 'UNPAID'
                        WHERE order_key = :cod_key
                    '''), params={"cod_key": cod["order_key"]})

                    await repository.create_delivery_invoice(db, dict(cod), {})
                    await repository.create_delivery_invoice(db, qr, {})
                    statuses = (await db.exec(text('''
                        SELECT o.order_code, o.order_payment_status
                        FROM ordering."order" o
                        WHERE o.order_key IN (:cod_key, :qr_key)
                    '''), params={"cod_key": cod["order_key"], "qr_key": qr["order_key"]})).mappings().all()
                    state_by_code = {row["order_code"]: row["order_payment_status"] for row in statuses}
                    assert state_by_code[cod["order_code"]] == "PAID"
                    assert state_by_code[qr["order_code"]] == "UNPAID"
                    raise RollbackCheck
            except RollbackCheck:
                pass
        await engine.dispose()

    asyncio.run(check())
