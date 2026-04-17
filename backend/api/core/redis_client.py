"""Global Redis client and helpers for evaluation progress tracking."""

import json
import logging

import redis
import redis.asyncio as redis_async

from api.core.config import settings

logger = logging.getLogger(__name__)
EVAL_PROGRESS_TTL = 3600

_redis_client: redis.Redis | None = None
_redis_async_client: redis_async.Redis | None = None

_REDIS_COMMON_KWARGS = dict(
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    socket_keepalive=True,
    health_check_interval=30,
    retry_on_timeout=True,
    ssl_cert_reqs=None,
)


def get_redis_client() -> redis.Redis | None:
    """Get the global Redis client, initializing if needed."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, **_REDIS_COMMON_KWARGS)
        except Exception as e:
            logger.error(f"Failed to initialize global Redis client: {e}")
            return None
    return _redis_client


async def get_async_redis_client() -> redis_async.Redis | None:
    global _redis_async_client
    if _redis_async_client is None:
        try:
            _redis_async_client = redis_async.from_url(
                settings.REDIS_URL, **_REDIS_COMMON_KWARGS
            )
        except Exception as e:
            logger.error(f"Failed to initialize async Redis client: {e}")
            return None
    return _redis_async_client


async def close_async_redis_client() -> None:
    global _redis_async_client
    if _redis_async_client is not None:
        try:
            await _redis_async_client.aclose()
        except Exception as e:
            logger.warning("Error closing async Redis client: %s", e)
        _redis_async_client = None


def set_eval_progress(
    trace_id: int,
    stage: str,
    percent: int | None,
    detail: str = "",
) -> None:
    """Set evaluation progress (sync, for Celery workers)."""
    try:
        r = get_redis_client()
        if r is None:
            logger.warning(
                f"Redis client unavailable, cannot set eval progress for trace {trace_id}"
            )
            return
        data = json.dumps({"stage": stage, "percent": percent, "detail": detail})
        r.set(f"eval_progress:{trace_id}", data, ex=EVAL_PROGRESS_TTL)
    except Exception as e:
        logger.warning(f"Failed to set eval progress for trace {trace_id}: {e}")


async def get_eval_progress(trace_id: int) -> dict | None:
    """Get evaluation progress (async, for FastAPI routes).

    Uses the sync client in a non-blocking way since the operation
    is a single fast GET and redis-py works fine from async context.
    """
    try:
        r = get_redis_client()
        if r is None:
            logger.warning(
                f"Redis client unavailable, cannot get eval progress for trace {trace_id}"
            )
            return None
        raw = r.get(f"eval_progress:{trace_id}")
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Failed to get eval progress for trace {trace_id}: {e}")
        return None


def clear_eval_progress(trace_id: int) -> None:
    """Remove evaluation progress key (sync, for cleanup)."""
    try:
        r = get_redis_client()
        if r is None:
            logger.warning(
                f"Redis client unavailable, cannot clear eval progress for trace {trace_id}"
            )
            return
        r.delete(f"eval_progress:{trace_id}")
    except Exception as e:
        logger.warning(f"Failed to clear eval progress for trace {trace_id}: {e}")
