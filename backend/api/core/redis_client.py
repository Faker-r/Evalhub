"""Redis helpers for evaluation progress tracking."""

import json

import redis

from api.core.config import settings

EVAL_PROGRESS_TTL = 3600  # 1 hour


def _get_sync_client() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def set_eval_progress(
    trace_id: int,
    stage: str,
    percent: int | None,
    detail: str = "",
) -> None:
    """Set evaluation progress (sync, for Celery workers)."""
    r = _get_sync_client()
    data = json.dumps({"stage": stage, "percent": percent, "detail": detail})
    r.set(f"eval_progress:{trace_id}", data, ex=EVAL_PROGRESS_TTL)


async def get_eval_progress(trace_id: int) -> dict | None:
    """Get evaluation progress (async, for FastAPI routes).

    Uses the sync client in a non-blocking way since the operation
    is a single fast GET and redis-py works fine from async context.
    """
    r = _get_sync_client()
    raw = r.get(f"eval_progress:{trace_id}")
    if raw is None:
        return None
    return json.loads(raw)


def clear_eval_progress(trace_id: int) -> None:
    """Remove evaluation progress key (sync, for cleanup)."""
    r = _get_sync_client()
    r.delete(f"eval_progress:{trace_id}")
