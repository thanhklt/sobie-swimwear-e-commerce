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
