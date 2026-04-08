"""Redis helpers for evaluation progress tracking."""

import json
import logging

import redis

from api.core.config import settings

logger = logging.getLogger(__name__)
EVAL_PROGRESS_TTL = 3600


def _get_sync_client() -> redis.Redis:
    logger.info(f"Creating Redis client with URL: {settings.REDIS_URL}")
    return redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
        retry_on_timeout=True,
        ssl_cert_reqs=None,
    )


def set_eval_progress(
    trace_id: int,
    stage: str,
    percent: int | None,
    detail: str = "",
) -> None:
    """Set evaluation progress (sync, for Celery workers)."""
    try:
        logger.info(f"Setting eval progress for trace {trace_id}: {stage} {percent}%")
        r = _get_sync_client()
        data = json.dumps({"stage": stage, "percent": percent, "detail": detail})
        r.set(f"eval_progress:{trace_id}", data, ex=EVAL_PROGRESS_TTL)
        logger.info(f"Successfully set eval progress for trace {trace_id}")
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning(f"Failed to set eval progress for trace {trace_id}: {e}")


async def get_eval_progress(trace_id: int) -> dict | None:
    """Get evaluation progress (async, for FastAPI routes).

    Uses the sync client in a non-blocking way since the operation
    is a single fast GET and redis-py works fine from async context.
    """
    try:
        logger.info(f"Getting eval progress for trace {trace_id}")
        r = _get_sync_client()
        raw = r.get(f"eval_progress:{trace_id}")
        if raw is None:
            logger.info(f"No eval progress found for trace {trace_id}")
            return None
        logger.info(f"Found eval progress for trace {trace_id}")
        return json.loads(raw)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning(f"Failed to get eval progress for trace {trace_id}: {e}")
        return None


def clear_eval_progress(trace_id: int) -> None:
    """Remove evaluation progress key (sync, for cleanup)."""
    try:
        logger.info(f"Clearing eval progress for trace {trace_id}")
        r = _get_sync_client()
        r.delete(f"eval_progress:{trace_id}")
        logger.info(f"Successfully cleared eval progress for trace {trace_id}")
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        logger.warning(f"Failed to clear eval progress for trace {trace_id}: {e}")
