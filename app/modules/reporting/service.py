"""Tổng hợp số liệu dashboard và bảng xếp hạng bán chạy cho trang chủ.

Module không có bảng riêng nên không có repository; mọi dữ liệu lấy qua service của module khác.
"""

import json
from collections import Counter
from collections.abc import Awaitable
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.modules.catalog import service as catalog
from app.modules.inventory import service as inventory
from app.modules.ordering import service as ordering
from app.modules.reporting.schemas import (
    Dashboard,
    HomeBestseller,
    LowStock,
    ReportPeriod,
    TopProduct,
)

HOME_BESTSELLERS_CACHE_KEY = "reporting:home_bestsellers"
HOME_BESTSELLERS_TTL_SECONDS = 30 * 60
_HOME_BESTSELLERS_WINDOW = timedelta(hours=168)
_HOME_BESTSELLERS_LIMIT = 15

ORDER_STATUS_LABELS = {
    "PENDING": "Chưa xử lý",
    "CONFIRMED": "Đã xác nhận",
    "AWAITING_PICKUP": "Chờ lấy hàng",
    "SHIPPING": "Đang giao",
    "DELIVERED": "Giao thành công",
    "DELIVERY_FAILED": "Giao không thành công",
    "CANCELLED": "Đã hủy",
}


class BestsellerCacheWriter(Protocol):
    def set(self, name: str, value: str, *, ex: int) -> Awaitable[object]: ...


# UC-37 Xem dashboard — Main Flow 3.1–3.6, AC-1–AC-6 và AC-9
# specs/use-cases/reporting/UC-37-view-dashboard.md
async def get_dashboard(period: ReportPeriod) -> Dashboard:
    from app.shared.database.engine import session_factory

    starts_at, ends_before = period.utc_bounds()
    async with session_factory() as db:
        # AC-1, AC-2, AC-9 — Tính doanh thu và lợi nhuận theo ngày giao thành công.
        # Đếm đơn theo ngày tạo để thống kê trạng thái.
        sales = await ordering.get_sales_stats(db, starts_at, ends_before)
        # AC-4–AC-6 — Luôn lấy tồn kho hiện tại, kể cả khi kỳ báo cáo trống.
        # Tiền nhập chỉ gồm phiếu đã xác nhận có ngày lập nằm trong kỳ.
        low_stock = await inventory.get_stock(db)
        purchase_totals = await inventory.get_purchase_totals(
            db, starts_at, ends_before
        )
        variants = await catalog.get_variants(
            db, set(sales.units_by_variant) | low_stock.keys()
        )

    # AC-3 — Cộng số lượng bán của các biến thể theo sản phẩm trước khi lấy Top 10.
    units_by_product: Counter[str] = Counter()
    product_names = {}
    for variant_key, quantity in sales.units_by_variant.items():
        variant = variants[variant_key]
        units_by_product[variant.product_code] += quantity
        product_names[variant.product_code] = variant.product_name

    ranked = sorted(units_by_product.items(), key=lambda row: (-row[1], row[0]))[:10]
    return Dashboard(
        revenue=sales.revenue,
        gross_profit=sales.revenue - sales.cost_of_goods,
        orders_by_status={
            status: sales.orders_by_status.get(status, 0)
            for status in ORDER_STATUS_LABELS
        },
        top_products=[
            TopProduct(code, product_names[code], quantity) for code, quantity in ranked
        ],
        low_stock=sorted(
            (
                LowStock(variants[key].sku, variants[key].product_name, quantity)
                for key, quantity in low_stock.items()
            ),
            key=lambda item: (item.quantity, item.sku),
        ),
        purchase_totals=purchase_totals,
    )


# UC-09 Xem trang chủ — AC-8, AC-9, AC-12, AC-13, AC-19 và AC-25
# specs/use-cases/catalog/UC-09-view-home-page.md
async def get_home_bestsellers(*, now: datetime | None = None) -> list[HomeBestseller]:
    """Tính Top 15 từ dữ liệu đơn hiện tại để catalog dùng khi cần fallback."""
    from app.shared.database.engine import session_factory

    if now is not None and now.utcoffset() is None:
        raise ValueError("Mốc tính bảng xếp hạng phải có múi giờ.")
    ends_at = now.astimezone(UTC) if now is not None else datetime.now(UTC)
    starts_at = ends_at - _HOME_BESTSELLERS_WINDOW

    async with session_factory() as db:
        variant_sales = await ordering.get_units_sold(db, starts_at, ends_at)
        variants = await catalog.get_variants(db, set(variant_sales))

    units_by_product: Counter[str] = Counter()
    latest_order_by_product: dict[str, datetime] = {}
    for variant_key, sale in variant_sales.items():
        product_id = variants[variant_key].product_code
        units_by_product[product_id] += sale.quantity
        latest_order_by_product[product_id] = max(
            latest_order_by_product.get(product_id, sale.latest_order_at),
            sale.latest_order_at,
        )

    # AC-13 — Khoảng cách ngắn hơn tới ends_at tương ứng với đơn đặt gần hơn.
    ranked = sorted(
        units_by_product,
        key=lambda product_id: (
            -units_by_product[product_id],
            ends_at - latest_order_by_product[product_id],
            product_id,
        ),
    )[:_HOME_BESTSELLERS_LIMIT]
    return [
        HomeBestseller(product_id, units_by_product[product_id])
        for product_id in ranked
    ]


# UC-09 Xem trang chủ — AC-6, AC-8 và AC-25
# specs/use-cases/catalog/UC-09-view-home-page.md
async def refresh_bestsellers(
    redis: BestsellerCacheWriter, *, now: datetime | None = None
) -> None:
    """Tính lại bảng xếp hạng và ghi Top 15 vào Redis trong 30 phút."""
    top = await get_home_bestsellers(now=now)
    payload = json.dumps([asdict(product) for product in top])
    await redis.set(
        HOME_BESTSELLERS_CACHE_KEY, payload, ex=HOME_BESTSELLERS_TTL_SECONDS
    )
