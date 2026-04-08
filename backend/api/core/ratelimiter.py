"""Distributed token-bucket rate limiting (Redis, async)."""

import logging
import math
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from api.core.config import settings
from api.core.redis_client import get_async_redis_client

logger = logging.getLogger(__name__)

_TOKEN_BUCKET_LUA = """
local raw = redis.call('GET', KEYS[1])
local capacity = tonumber(ARGV[1])
local fill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])

if fill_rate == nil or fill_rate <= 0 then
  fill_rate = 0.000001
end

local tokens, last_ts
if raw == false then
  tokens = capacity
  last_ts = now
else
  local comma = string.find(raw, ',', 1, true)
  if comma == nil then
    tokens = capacity
    last_ts = now
  else
    tokens = tonumber(string.sub(raw, 1, comma - 1))
    last_ts = tonumber(string.sub(raw, comma + 1))
    if tokens == nil or last_ts == nil then
      tokens = capacity
      last_ts = now
    end
  end
end

local elapsed = now - last_ts
if elapsed < 0 then
  elapsed = 0
end

tokens = math.min(capacity, tokens + math.floor(fill_rate * elapsed))

if tokens <= 0 then
  local wait = 1.0 / fill_rate
  if wait < 1 then
    wait = 1
  end
  return {0, math.ceil(wait)}
end

tokens = tokens - 1
redis.call('SET', KEYS[1], tokens .. ',' .. now, 'EX', ttl)
return {1, 0}
"""


def default_rate_limit_key(request: Request) -> str:
    if settings.RATE_LIMIT_BEHIND_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


class AsyncRateLimiter:
    async def allow_request(self, key: str) -> tuple[bool, int]:
        r = await get_async_redis_client()
        if r is None:
            return settings.RATE_LIMIT_FAIL_OPEN, 1

        redis_key = f"{settings.RATE_LIMIT_KEY_PREFIX}{key}"
        now = time.time()
        cap = settings.RATE_LIMIT_BUCKET_CAPACITY
        fill = settings.RATE_LIMIT_FILL_RATE
        ttl = settings.RATE_LIMIT_TTL_SECONDS

        result = await r.eval(
            _TOKEN_BUCKET_LUA,
            1,
            redis_key,
            str(cap),
            str(fill),
            str(now),
            str(ttl),
        )
        allowed = int(result[0]) == 1
        retry_after = int(result[1]) if result[1] else 0
        return allowed, retry_after


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, key_generator=default_rate_limit_key):
        super().__init__(app)
        self.key_generator = key_generator
        self._limiter = AsyncRateLimiter()
        self._excluded_paths = frozenset(settings.RATE_LIMIT_EXCLUDE_PATHS)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self._excluded_paths:
            return await call_next(request)

        try:
            allowed, retry_after = await self._limiter.allow_request(
                self.key_generator(request)
            )
        except Exception as e:
            logger.warning("Rate limit check failed: %s", e)
            allowed = settings.RATE_LIMIT_FAIL_OPEN
            retry_after = max(
                1, math.ceil(1 / max(settings.RATE_LIMIT_FILL_RATE, 1e-9))
            )

        if allowed:
            return await call_next(request)

        if retry_after <= 0:
            retry_after = max(
                1, math.ceil(1 / max(settings.RATE_LIMIT_FILL_RATE, 1e-9))
            )

        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too Many Requests",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )
