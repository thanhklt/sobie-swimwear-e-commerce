"""Các truy vấn công khai catalog dùng bởi module khác."""

from app.modules.catalog import repository


async def invoice_variant_details(db, variant_keys):
    """Lấy thông tin catalog cần chụp vào hóa đơn cho các dòng đơn."""
    return await repository.invoice_variant_details(db, variant_keys)


async def active_product_key(db, product_id: str):
    """Trả khóa sản phẩm đang bán cho promotion; catalog vẫn sở hữu truy vấn."""
    return await repository.active_product_key(db, product_id)


async def product_ids_by_keys(db, product_keys):
    return await repository.product_ids_by_keys(db, product_keys)
