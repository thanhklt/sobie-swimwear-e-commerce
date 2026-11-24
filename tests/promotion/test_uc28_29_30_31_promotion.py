"""Kiểm tra tiêu chí UC-28..31, UC-36 và UC-40 ở tầng nghiệp vụ."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
import os

import pytest

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


def test_uc29_uc30_ac11_end_of_selected_day_asia_ho_chi_minh():
    """End date 20/11 ICT applies until exclusive 00:00 21/11 ICT."""
    from zoneinfo import ZoneInfo
    from datetime import date

    local = ZoneInfo("Asia/Ho_Chi_Minh")
    end_bound = promotion_service._as_utc(date(2026, 11, 20), next_day=True)
    assert end_bound == datetime(2026, 11, 20, 17, 0, tzinfo=UTC)  # 00:00 21/11 ICT

    just_before = datetime(2026, 11, 20, 16, 59, 59, tzinfo=UTC)  # 23:59:59 20/11 ICT
    at_boundary = end_bound
    row = {
        "promotion_status": "ENABLED",
        "promotion_start_date": promotion_service._as_utc(date(2026, 11, 1)),
        "promotion_end_date": end_bound,
        "promotion_used_amount": 0,
        "promotion_quantity": 10,
    }
    assert promotion_service.display_status(row, just_before) == "Đang hiệu lực"
    assert promotion_service.display_status(row, at_boundary) == "Đã kết thúc"
    assert just_before.astimezone(local).date().isoformat() == "2026-11-20"
    assert at_boundary.astimezone(local).date().isoformat() == "2026-11-21"


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


def test_uc31_ac10_reconfirm_when_only_source_changes():
    previous = {"selected_discount": 40_000, "selected_source": "CODE", "selected_promotion_id": "KM-0002"}
    current = {"selected_discount": 40_000, "selected_source": "ORDER", "selected_promotion_id": "KM-0001"}
    assert promotion_service.quote_requires_reconfirm(previous, current) is True
    same = {"selected_discount": 40_000, "selected_source": "CODE", "selected_promotion_id": "KM-0002"}
    assert promotion_service.quote_requires_reconfirm(previous, same) is False


def test_uc31_invalid_voucher_still_keeps_best_order_promotion(monkeypatch):
    async def eligible(_db, _subtotal, _now):
        return [{"promotion_key": "order-key", "promotion_id": "KM-0003",
                 "discount_percentage": Decimal("10")}]

    async def no_voucher(_db, _code):
        return None

    monkeypatch.setattr(promotion_service.repository, "find_eligible_order_promotions", eligible)
    monkeypatch.setattr(promotion_service.repository, "find_code_promotion", no_voucher)
    quote = asyncio.run(promotion_service.quote_order_discount(
        object(), 500_000, voucher_code="KM-0001",
    ))
    assert quote["selected_source"] == "ORDER"
    assert quote["selected_promotion_id"] == "KM-0003"
    assert quote["selected_discount"] == 50_000
    assert quote["notice"] == "Voucher không hợp lệ."


def test_uc31_ac11_refund_applies_to_order_and_voucher(monkeypatch):
    calls = []

    async def decrement(_db, key):
        calls.append(key)

    monkeypatch.setattr(promotion_service.repository, "decrement_used", decrement)
    asyncio.run(promotion_service.refund_promotion(object(), "order-promo-key"))
    asyncio.run(promotion_service.refund_promotion(object(), "voucher-promo-key"))
    assert calls == ["order-promo-key", "voucher-promo-key"]


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
                    quote = await promotion_service.quote_order_discount(
                        db, 100_000, voucher_code="KM-0001", now=now,
                    )
                    assert quote["selected_source"] == "ORDER"
                    assert quote["selected_discount"] > 0
                    assert quote["notice"] == "Voucher không hợp lệ."
                    assert product["promotion_id"].startswith("KM-")
                    assert voucher["promotion_id"].startswith("KM-")
                    raise RollbackCheck
            except RollbackCheck:
                pass
        await engine.dispose()

    asyncio.run(check())

def test_uc28_29_30_ac2_admin_template_has_confirmation_and_no_edit(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.modules.promotion import router as promotion_router
    from app.modules.catalog import service as catalog_service

    async def rows(_db, *_args):
        return []
    async def products(_db):
        return []
    async def fake_db():
        yield object()

    monkeypatch.setattr(promotion_service, "list_promotions", rows)
    monkeypatch.setattr(catalog_service, "active_products_for_promotion", products)
    app.dependency_overrides[promotion_router.employee_only] = lambda: object()
    app.dependency_overrides[promotion_router._db] = fake_db
    try:
        response = TestClient(app).get("/admin/promotions")
    finally:
        app.dependency_overrides.pop(promotion_router.employee_only, None)
        app.dependency_overrides.pop(promotion_router._db, None)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "Xác nhận tạo" in response.text
    assert "đã tạo thì không thể sửa" in response.text
    assert "Số lượt tối đa" in response.text
    assert "Sửa chương trình" not in response.text
    assert "Thử tính ưu đãi cho đơn hàng" in response.text
    assert "/admin/promotions/quote-preview" in response.text
    assert "label[hidden],[hidden]{display:none!important}" in response.text
    assert "control.disabled=!show" in response.text


@pytest.mark.parametrize("query", [
    "?kind=PRODUCT&date_from=&date_to=",
    "?date_from=2026-11-01&date_to=",
    "?date_from=&date_to=2026-11-30",
    "?date_from=not-a-date&date_to=",
])
def test_promotion_list_optional_date_filters_do_not_return_422(query, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.modules.promotion import router as promotion_router
    from app.modules.catalog import service as catalog_service

    async def rows(_db, *_args):
        return []
    async def products(_db):
        return []
    async def fake_db():
        yield object()

    monkeypatch.setattr(promotion_service, "list_promotions", rows)
    monkeypatch.setattr(catalog_service, "active_products_for_promotion", products)
    app.dependency_overrides[promotion_router.employee_only] = lambda: object()
    app.dependency_overrides[promotion_router._db] = fake_db
    try:
        response = TestClient(app).get("/admin/promotions" + query)
    finally:
        app.dependency_overrides.pop(promotion_router.employee_only, None)
        app.dependency_overrides.pop(promotion_router._db, None)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    if "not-a-date" in query:
        assert "Ngày lọc không hợp lệ." in response.text
