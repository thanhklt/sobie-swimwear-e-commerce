"""Ca nghiệm thu HTTP của UC-37, sử dụng dữ liệu PostgreSQL thực.

AC-4 và AC-6 sử dụng ngưỡng tồn kho 5 theo dữ liệu nghiệm thu của UC-37.
"""

from datetime import UTC, datetime

import pytest

NOVEMBER = ("2026-11-01", "2026-11-30")
DECEMBER = ("2026-12-01", "2026-12-31")
IN_NOVEMBER = datetime(2026, 11, 20, 10, tzinfo=UTC)


def _request_dashboard(client, path, period, *, htmx=False, previous_period=None):
    start_date, end_date = period
    params = {"start_date": start_date, "end_date": end_date}
    if previous_period:
        params["previous_start_date"], params["previous_end_date"] = previous_period
    return client.get(
        path,
        params=params,
        headers={"HX-Request": "true"} if htmx else None,
        follow_redirects=False,
    )


def _dashboard(response):
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    view = response.context["dashboard"]
    return {
        "revenue": view.revenue,
        "gross_profit": view.gross_profit,
        "orders_by_status": view.orders_by_status,
        "top_products": [
            (product.name, product.quantity) for product in view.top_products
        ],
        "low_stock": [(variant.sku, variant.quantity) for variant in view.low_stock],
        "purchase_totals": [
            (supplier.supplier_code, supplier.supplier_name, supplier.amount)
            for supplier in view.purchase_totals
        ],
    }


@pytest.fixture
def employee_dashboard(dashboard_db, dashboard_path):
    client, data = dashboard_db
    data.sign_in(client, "employee")
    return client, data, dashboard_path


# UC-37 Xem dashboard — AC-1: Doanh thu và lợi nhuận gộp
def test_uc37_ac1_revenue_and_gross_profit(employee_dashboard):
    client, data, path = employee_dashboard
    variant, _ = data.product("Áo bơi A")
    data.order(
        "DELIVERED",
        IN_NOVEMBER,
        delivered_at=IN_NOVEMBER,
        lines=[(variant, 2, 120_000)],
        subtotal=400_000,
        discount=50_000,
        unit_price=225_000,
    )
    data.order(
        "CANCELLED",
        IN_NOVEMBER,
        lines=[(variant, 1, 120_000)],
        subtotal=300_000,
        unit_price=300_000,
    )

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert report["revenue"] == 400_000
    assert report["gross_profit"] == 160_000


# UC-37 Xem dashboard — AC-2: Số đơn theo trạng thái
def test_uc37_ac2_order_count_by_status(employee_dashboard):
    client, data, path = employee_dashboard
    for _ in range(3):
        data.order("PENDING", IN_NOVEMBER)
    for _ in range(2):
        data.order("DELIVERED", IN_NOVEMBER, delivered_at=IN_NOVEMBER)
    data.order("CANCELLED", IN_NOVEMBER)
    data.order("CONFIRMED", datetime(2026, 10, 20, tzinfo=UTC))

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert report["orders_by_status"] == {
        "PENDING": 3,
        "CONFIRMED": 0,
        "AWAITING_PICKUP": 0,
        "SHIPPING": 0,
        "DELIVERED": 2,
        "DELIVERY_FAILED": 0,
        "CANCELLED": 1,
    }


# UC-37 Xem dashboard — AC-3: Sản phẩm bán chạy
@pytest.mark.parametrize(
    ("sales", "expected"),
    [
        ([("A", 6), ("B", 8), ("C", 2)], [("B", 8), ("A", 6), ("C", 2)]),
        (
            list(zip("ABCDEFGHIJK", range(1, 12), strict=True)),
            [
                ("K", 11),
                ("J", 10),
                ("I", 9),
                ("H", 8),
                ("G", 7),
                ("F", 6),
                ("E", 5),
                ("D", 4),
                ("C", 3),
                ("B", 2),
            ],
        ),
    ],
    ids=["three-products", "eleven-products"],
)
def test_uc37_ac3_bestsellers_sorted_and_limited(employee_dashboard, sales, expected):
    client, data, path = employee_dashboard
    lines = []
    for name, quantity in sales:
        variant_status = "INACTIVE" if name == "B" else "ACTIVE"
        variant_key, _ = data.product(name, variant_status=variant_status)
        lines.append((variant_key, quantity, 120_000))
    data.order(
        "DELIVERED",
        IN_NOVEMBER,
        delivered_at=IN_NOVEMBER,
        lines=lines,
        subtotal=sum(quantity for _, quantity in sales) * 200_000,
    )

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert report["top_products"] == expected


# UC-37 Xem dashboard — AC-4: Tồn kho thấp
def test_uc37_ac4_low_stock_includes_threshold(employee_dashboard):
    client, data, path = employee_dashboard
    _, sku_x = data.product("X", stock=3)
    _, sku_y = data.product("Y", stock=5)
    data.product("Z", stock=6)

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert dict(report["low_stock"]) == {sku_x: 3, sku_y: 5}


# UC-37 Xem dashboard — AC-5: Tiền nhập hàng theo nhà cung cấp
def test_uc37_ac5_purchase_totals_only_include_confirmed_receipts_created_in_period(
    employee_dashboard,
):
    client, data, path = employee_dashboard
    supplier = data.supplier()
    variant, _ = data.product("Áo bơi A")
    data.receipt(supplier, variant, "CONFIRMED", 3_000_000, IN_NOVEMBER)
    data.receipt(supplier, variant, "CONFIRMED", 2_000_000, IN_NOVEMBER)
    data.receipt(supplier, variant, "DRAFT", 1_000_000, IN_NOVEMBER)
    data.receipt(
        supplier, variant, "CONFIRMED", 2_000_000, datetime(2026, 10, 30, tzinfo=UTC)
    )

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert report["purchase_totals"] == [("NCC-0001", "Nhà cung cấp X", 5_000_000)]


# UC-37 Xem dashboard — AC-6: Kỳ không có dữ liệu
def test_uc37_ac6_empty_period_still_reports_low_stock(employee_dashboard):
    client, data, path = employee_dashboard
    _, sku_x = data.product("X", stock=3)
    data.product("Y", stock=6)

    report = _dashboard(_request_dashboard(client, path, NOVEMBER))

    assert report["revenue"] == report["gross_profit"] == 0
    assert len(report["orders_by_status"]) == 7
    assert all(count == 0 for count in report["orders_by_status"].values())
    assert not report["top_products"]
    assert not report["purchase_totals"]
    assert dict(report["low_stock"]) == {sku_x: 3}


# UC-37 Xem dashboard — AC-7: Khoảng thời gian không hợp lệ
@pytest.mark.parametrize(
    "invalid_period",
    [("2026-12-02", "2026-12-01"), ("2026-12-01", "2026-12-01")],
    ids=["reversed-dates", "equal-dates"],
)
def test_uc37_ac7_invalid_period_preserves_report(employee_dashboard, invalid_period):
    client, data, path = employee_dashboard
    variant, _ = data.product("Áo bơi A")
    data.order(
        "DELIVERED",
        IN_NOVEMBER,
        delivered_at=IN_NOVEMBER,
        lines=[(variant, 2, 120_000)],
        subtotal=400_000,
    )
    previous_result = _dashboard(_request_dashboard(client, path, NOVEMBER))
    assert previous_result["revenue"] == 400_000

    invalid = _request_dashboard(client, path, invalid_period, htmx=True)

    assert "ngày bắt đầu phải nhỏ hơn ngày kết thúc" in invalid.text.casefold()
    assert invalid.headers["HX-Retarget"] == "#dashboard-errors"
    assert "dashboard" not in invalid.context

    full_page = _request_dashboard(
        client, path, invalid_period, previous_period=NOVEMBER
    )
    assert "ngày bắt đầu phải nhỏ hơn ngày kết thúc" in full_page.text.casefold()
    assert _dashboard(full_page) == previous_result


# UC-37 Xem dashboard — AC-8: Vai trò không được phép
@pytest.mark.parametrize(
    "role, denied_statuses", [("customer", {303, 401, 403}), ("admin", {403})]
)
def test_uc37_ac8_rejects_non_employee(
    dashboard_db, dashboard_path, role, denied_statuses
):
    client, data = dashboard_db
    data.sign_in(client, role)

    response = _request_dashboard(client, dashboard_path, NOVEMBER)

    assert response.status_code in denied_statuses
    assert "dashboard" not in getattr(response, "context", {})


# UC-37 Xem dashboard — AC-9: Ghi nhận theo ngày giao thành công
def test_uc37_ac9_delivery_date_sets_reporting_month(employee_dashboard):
    client, data, path = employee_dashboard
    variant, _ = data.product("A")
    # 18:00 UTC ngày 30/11 là 01:00 ngày 01/12 theo Asia/Ho_Chi_Minh.
    data.order(
        "DELIVERED",
        datetime(2026, 11, 30, 10, tzinfo=UTC),
        delivered_at=datetime(2026, 11, 30, 18, tzinfo=UTC),
        lines=[(variant, 2, 120_000)],
        subtotal=400_000,
    )

    november = _dashboard(_request_dashboard(client, path, NOVEMBER))
    december = _dashboard(_request_dashboard(client, path, DECEMBER))

    assert november["revenue"] == november["gross_profit"] == 0
    assert not november["top_products"]
    assert december["revenue"] == 400_000
    assert december["gross_profit"] == 160_000
    assert december["top_products"] == [("A", 2)]
