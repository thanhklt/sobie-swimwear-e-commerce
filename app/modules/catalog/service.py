"""Tầng Service của module catalog: nghiệp vụ và điều phối transaction.

Service công khai cho module khác:
- Lấy thông tin biến thể và giá bán hiện tại (cho shopping, ordering).
- Kiểm tra sản phẩm / biến thể đang bán.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from app.modules.catalog import repository
from app.modules.catalog.home_sample import HOME_PAGE
from app.modules.catalog.schemas import HomePage


async def get_cart_variants(db, variant_keys):
    return await repository.find_cart_variants(db, variant_keys)


def get_home_page() -> HomePage:
    return HOME_PAGE
