"""Tổng hợp số liệu báo cáo cho dashboard Nhân viên.

Module không có bảng riêng nên không có repository; mọi dữ liệu lấy qua service của module khác.
"""

from collections import Counter

from app.modules.catalog import service as catalog
from app.modules.inventory import service as inventory
from app.modules.ordering import service as ordering
from app.modules.reporting.schemas import Dashboard, LowStock, ReportPeriod, TopProduct

ORDER_STATUS_LABELS = {
    "PENDING": "Chưa xử lý",
    "CONFIRMED": "Đã xác nhận",
    "AWAITING_PICKUP": "Chờ lấy hàng",
    "SHIPPING": "Đang giao",
    "DELIVERED": "Giao thành công",
    "DELIVERY_FAILED": "Giao không thành công",
    "CANCELLED": "Đã hủy",
}


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
