"""Tầng Service của module catalog: nghiệp vụ và điều phối transaction.
Hiện triển khai service đọc, khóa và tăng phiên bản cache phục vụ inventory.

Service công khai cho module khác:
- Lấy thông tin biến thể và giá bán hiện tại (cho shopping, ordering).
- Kiểm tra sản phẩm / biến thể đang bán.

Chỉ gọi repository của chính module này; dữ liệu module khác lấy qua service của module đó.
"""

from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.catalog import repository

CATALOG_VERSION_KEY = "catalog:version"
CATALOG_CACHE_TTL = 300


async def get_inventory_variants(db: AsyncSession, variant_keys: list[UUID], *, lock: bool = False) -> list[dict]:
    """Read current metadata, including inactive items; optional locks share caller transaction."""
    return await repository.get_inventory_variants(db, variant_keys, lock=lock)


async def list_inventory_variants(db: AsyncSession, *, q: str = "", category_key: UUID | None = None,
                                  offset: int = 0, limit: int | None = 20) -> tuple[list[dict], int]:
    return await repository.list_inventory_variants(db, q=q, category_key=category_key, offset=offset, limit=limit)


async def inventory_categories(db: AsyncSession) -> list[dict]:
    return await repository.inventory_categories(db)


async def bump_catalog_version() -> None:
    """Invalidate shared public-data keys after commit; existing keys expire within 300 seconds."""
    from redis.asyncio import Redis
    from redis.asyncio.retry import Retry
    from redis.backoff import NoBackoff
    from app.shared.config.settings import Config

    async with Redis.from_url(Config.REDIS_URL, socket_connect_timeout=1, socket_timeout=1,
                              retry=Retry(NoBackoff(), 0)) as client:
        await client.incr(CATALOG_VERSION_KEY)
