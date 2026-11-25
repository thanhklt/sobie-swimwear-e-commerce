"""Tầng Service của module catalog: nghiệp vụ và điều phối transaction. Chưa triển khai.

Service công khai cho module khác:
- Lấy thông tin biến thể và giá bán hiện tại (cho shopping, ordering).
- Kiểm tra sản phẩm / biến thể đang bán.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from app.modules.catalog import repository


async def get_cart_variants(db, variant_keys):
    return await repository.find_cart_variants(db, variant_keys)
