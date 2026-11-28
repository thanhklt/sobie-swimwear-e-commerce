"""Khởi tạo client Redis dùng chung.

Client được tạo lười khi gọi `get_redis()` lần đầu, nên thiếu Redis không làm hỏng lúc khởi động app.
`main.py` truyền `get_redis` cho module cần Redis và gọi `close_redis()` khi tắt server.
"""

from functools import lru_cache

from redis.asyncio import Redis

from app.config.settings import Config


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    if not Config.REDIS_URL:
        raise RuntimeError("REDIS_URL is required for registration")
    return Redis.from_url(
        Config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


async def close_redis() -> None:
    if get_redis.cache_info().currsize:
        await get_redis().aclose()
        get_redis.cache_clear()
