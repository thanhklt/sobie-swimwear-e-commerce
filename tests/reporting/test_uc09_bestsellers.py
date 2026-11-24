"""Ca nghiệm thu phần reporting của UC-09 với dữ liệu đơn PostgreSQL.

Đặc tả: specs/use-cases/catalog/UC-09-view-home-page.md.

Câu hỏi mở [GD]: tên key Redis cho catalog đọc có dùng
reporting:home_bestsellers như hằng HOME_BESTSELLERS_CACHE_KEY không?
"""

import json
from datetime import UTC, datetime, timedelta
from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.modules.reporting import service as reporting

NOW = datetime(2026, 11, 24, 10, tzinfo=UTC)


def _refresh_rows(data):
    redis = SimpleNamespace(set=AsyncMock())
    data.portal.call(partial(reporting.refresh_bestsellers, redis, now=NOW))
    redis.set.assert_awaited_once()
    (key, payload), options = redis.set.await_args
    assert key == reporting.HOME_BESTSELLERS_CACHE_KEY
    assert options["ex"] == 30 * 60
    rows = json.loads(payload)
    assert all(row.keys() == {"product_id", "quantity"} for row in rows)
    return [(row["product_id"], row["quantity"]) for row in rows]


def _fallback_rows(data):
    rows = data.portal.call(partial(reporting.get_home_bestsellers, now=NOW))
    return [(row.product_id, row.quantity) for row in rows]


def _place_order(data, placed_at, *items, status="PENDING", delivered_at=None):
    data.order(
        status,
        placed_at,
        delivered_at=delivered_at,
        lines=[(variant, quantity, 90_000) for variant, quantity in items],
        subtotal=sum(quantity for _, quantity in items) * 200_000,
    )


# UC-09 Xem trang chủ — AC-6: Reporting ghi danh sách rỗng để catalog ẩn khối.
def test_uc09_ac6_refresh_caches_empty_ranking_when_no_orders_qualify(reporting_db):
    _, data = reporting_db
    variant, _ = data.product("A")
    _place_order(data, NOW - timedelta(hours=1), (variant, 3), status="CANCELLED")

    assert _refresh_rows(data) == []


# UC-09 Xem trang chủ — AC-8: Xếp bán chạy theo tổng số lượng bán.
def test_uc09_ac8_refresh_ranks_by_units_across_variants(reporting_db):
    _, data = reporting_db
    small_a, _ = data.product("A")
    large_a = data.add_large_variant(small_a)
    variant_b, _ = data.product("B")
    placed_at = NOW - timedelta(hours=2)
    _place_order(data, placed_at, (small_a, 2), (large_a, 3))
    _place_order(data, placed_at, (variant_b, 1))
    _place_order(data, placed_at, (variant_b, 1))

    assert _refresh_rows(data) == [("SP-0001", 5), ("SP-0002", 2)]


# UC-09 Xem trang chủ — AC-9: Chỉ tính đơn đặt trong 168 giờ gần nhất (UTC).
def test_uc09_ac9_filters_by_order_creation_in_rolling_window(reporting_db):
    _, data = reporting_db
    inside, _ = data.product("Trong kỳ")
    outside, _ = data.product("Ngoài kỳ")
    _place_order(data, NOW - timedelta(hours=167, minutes=59), (inside, 3))
    _place_order(
        data,
        NOW - timedelta(hours=170),
        (outside, 8),
        status="DELIVERED",
        delivered_at=NOW - timedelta(hours=1),
    )

    assert _fallback_rows(data) == [("SP-0001", 3)]


# UC-09 Xem trang chủ — AC-12: Chỉ tính các trạng thái đơn hợp lệ.
def test_uc09_ac12_counts_only_eligible_order_statuses(reporting_db):
    _, data = reporting_db
    accepted, _ = data.product("Đơn hợp lệ")
    cancelled, _ = data.product("Đơn đã hủy")
    failed, _ = data.product("Đơn giao thất bại")
    placed_at = NOW - timedelta(hours=3)
    for status in ("PENDING", "CONFIRMED", "AWAITING_PICKUP", "SHIPPING", "DELIVERED"):
        _place_order(
            data,
            placed_at,
            (accepted, 2),
            status=status,
            delivered_at=NOW - timedelta(hours=1) if status == "DELIVERED" else None,
        )
    _place_order(data, placed_at, (cancelled, 20), status="CANCELLED")
    _place_order(data, placed_at, (failed, 30), status="DELIVERY_FAILED")

    assert _fallback_rows(data) == [("SP-0001", 10)]


# UC-09 Xem trang chủ — AC-13: Hòa số lượng, ưu tiên đơn đặt gần nhất.
def test_uc09_ac13_prefers_latest_order_when_quantities_tie(reporting_db):
    _, data = reporting_db
    older, _ = data.product("Đơn đặt sớm hơn")
    newer, _ = data.product("Đơn đặt muộn hơn")
    _place_order(data, NOW - timedelta(hours=2), (older, 4))
    _place_order(data, NOW - timedelta(hours=1), (newer, 4))

    assert _fallback_rows(data) == [("SP-0002", 4), ("SP-0001", 4)]


# UC-09 Xem trang chủ — AC-13: Hòa số lượng và thời điểm, xếp theo product_id.
def test_uc09_ac13_prefers_smaller_product_id_when_latest_order_ties(reporting_db):
    _, data = reporting_db
    smaller, _ = data.product("Mã nhỏ hơn")
    larger, _ = data.product("Mã lớn hơn")
    _place_order(data, NOW - timedelta(hours=1), (larger, 3), (smaller, 3))

    assert _fallback_rows(data) == [("SP-0001", 3), ("SP-0002", 3)]


# UC-09 Xem trang chủ — AC-19: Fallback lấy bảng xếp hạng từ dữ liệu đơn hiện hành.
def test_uc09_ac19_fallback_recalculates_from_database_without_redis(reporting_db):
    _, data = reporting_db
    variant, _ = data.product("A")
    placed_at = NOW - timedelta(hours=1)
    _place_order(data, placed_at, (variant, 2))
    assert _fallback_rows(data) == [("SP-0001", 2)]

    _place_order(data, placed_at, (variant, 3))

    assert _fallback_rows(data) == [("SP-0001", 5)]


# UC-09 Xem trang chủ — AC-25: Reporting chuyển tối đa Top 15 để catalog lọc.
@pytest.mark.parametrize(
    "read_rows", [_refresh_rows, _fallback_rows], ids=["redis", "db"]
)
def test_uc09_ac25_limits_candidates_before_catalog_checks_status(
    reporting_db, read_rows
):
    _, data = reporting_db
    items = []
    for index in range(1, 17):
        variant, _ = data.product(
            f"Sản phẩm {index}", variant_status="INACTIVE" if index == 1 else "ACTIVE"
        )
        items.append((variant, 17 - index))
    _place_order(data, NOW - timedelta(hours=1), *items)

    assert read_rows(data) == [
        (f"SP-{index:04d}", 17 - index) for index in range(1, 16)
    ]
