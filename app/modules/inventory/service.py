"""Nghiệp vụ tồn kho công khai cho module ordering."""

from app.modules.inventory import repository


async def restore_failed_delivery_stock(db, variant_lines):
    """Cộng lại từng dòng hàng; caller giữ transaction cùng cập nhật đơn."""
    for variant_key, quantity in variant_lines:
        await repository.restore_variant_stock(db, variant_key, quantity)
