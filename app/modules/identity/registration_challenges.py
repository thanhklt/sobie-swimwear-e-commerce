"""Lưu và chuyển trạng thái xác minh dùng một lần trong Redis."""

from functools import lru_cache
from typing import Protocol

from redis.asyncio import Redis

from app.config.settings import Config

_COMPARE_AND_SET = """
local existing = redis.call('GET', KEYS[1])
if ARGV[1] == 'absent' then
    if existing then return 0 end
elseif existing ~= ARGV[2] then
    return 0
end
if ARGV[3] == 'delete' then
    redis.call('DEL', KEYS[1])
else
    redis.call('SET', KEYS[1], ARGV[4], 'EX', ARGV[5])
end
return 1
"""


_EXHAUST_OTP = """
if redis.call('GET', KEYS[1]) ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])
if redis.call('PTTL', KEYS[2]) < tonumber(ARGV[4]) * 1000 then
    local claim = redis.call('GET', KEYS[2]) or 'locked'
    redis.call('SET', KEYS[2], claim, 'EX', ARGV[4])
end
return 1
"""


_LOGIN_ATTEMPT = """
local clock = redis.call('TIME')
local now = tonumber(clock[1]) * 1000 + math.floor(tonumber(clock[2]) / 1000)
while true do
    local oldest = redis.call('LINDEX', KEYS[1], 0)
    if not oldest or tonumber(oldest) > now - 60000 then break end
    redis.call('LPOP', KEYS[1])
end
local attempts = redis.call('LLEN', KEYS[1])
if attempts >= 5 then return 6 end
redis.call('RPUSH', KEYS[1], tostring(now))
redis.call('PEXPIRE', KEYS[1], 60000)
return attempts + 1
"""


class ChallengeStore(Protocol):
    async def get(self, key: str) -> str | None: ...

    async def compare_and_set(
        self, key: str, expected: str | None, value: str | None, ttl: int = 0
    ) -> bool: ...

    async def exhaust_otp(
        self, key: str, expected: str, value: str, ttl: int, *,
        cooldown_key: str, cooldown_seconds: int,
    ) -> bool: ...


class RedisChallengeStore:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def count_password_attempt(self, ip_key: str) -> int:
        return await self.redis.eval(_LOGIN_ATTEMPT, 1, f'identity:password-login:{ip_key}')

    async def compare_and_set(
        self, key: str, expected: str | None, value: str | None, ttl: int = 0
    ) -> bool:
        result = await self.redis.eval(
            _COMPARE_AND_SET,
            1,
            key,
            "absent" if expected is None else "present",
            expected or "",
            "delete" if value is None else "set",
            value or "",
            ttl,
        )
        return bool(result)

    async def exhaust_otp(
        self, key: str, expected: str, value: str, ttl: int, *,
        cooldown_key: str, cooldown_seconds: int,
    ) -> bool:
        return bool(await self.redis.eval(
            _EXHAUST_OTP, 2, key, cooldown_key, expected, value, ttl, cooldown_seconds
        ))


@lru_cache(maxsize=1)
def get_challenge_store() -> RedisChallengeStore:
    if not Config.REDIS_URL:
        raise RuntimeError("REDIS_URL is required for registration")
    return RedisChallengeStore(
        Redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    )


async def close_challenge_store() -> None:
    if get_challenge_store.cache_info().currsize:
        await get_challenge_store().redis.aclose()
        get_challenge_store.cache_clear()
