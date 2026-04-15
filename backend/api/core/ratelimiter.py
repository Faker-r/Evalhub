"""Application-wide rate limiting via SlowAPI (Redis-backed, shared per client).

``REDIS_URL`` is passed to ``limits`` as ``storage_uri`` (``redis.from_url``).
Both ``redis://`` and ``rediss://`` (TLS) are supported; extra client kwargs match
``api.core.redis_client`` so TLS URLs behave the same as the rest of the app.
"""

from slowapi import Limiter
from starlette.requests import Request

from api.core.config import settings

# Same TLS/socket defaults as redis_client._REDIS_COMMON_KWARGS for redis.from_url.
_REDIS_STORAGE_OPTIONS = {
    "decode_responses": True,
    "socket_connect_timeout": 5,
    "socket_timeout": 5,
    "socket_keepalive": True,
    "health_check_interval": 30,
    "retry_on_timeout": True,
    "ssl_cert_reqs": None,
}


def rate_limit_key(request: Request) -> str:
    if settings.RATE_LIMIT_BEHIND_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


limiter = Limiter(
    key_func=rate_limit_key,
    application_limits=[settings.RATE_LIMIT],
    default_limits=[],
    storage_uri=settings.REDIS_URL,
    storage_options=_REDIS_STORAGE_OPTIONS,
    key_prefix=settings.RATE_LIMIT_KEY_PREFIX,
    swallow_errors=settings.RATE_LIMIT_FAIL_OPEN,
    strategy=settings.RATE_LIMIT_STRATEGY,
)
