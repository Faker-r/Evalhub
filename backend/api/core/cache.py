import json
import logging
from typing import Any, Callable, TypeVar
from pydantic import BaseModel

from api.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _serialize(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return json.dumps(value)


def _deserialize(
    raw: str, revive: type[T] | Callable[[Any], T] | None = None
) -> T | dict[str, Any]:
    data = json.loads(raw)
    if revive is None:
        return data
    if isinstance(revive, type) and issubclass(revive, BaseModel):
        return revive.model_validate(data)
    return revive(data)


class CacheService:
    def _get_client(self):
        return get_redis_client()

    def get(
        self, key: str, revive: type[T] | Callable[[Any], T] | None = None
    ) -> T | dict[str, Any] | None:
        try:
            client = self._get_client()
            if client is None:
                logger.warning(f"Redis client unavailable for GET key {key}")
                return None
            raw = client.get(key)
            if raw is None:
                return None
            return _deserialize(raw, revive)
        except Exception as e:
            logger.warning(f"Redis GET failed for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        try:
            client = self._get_client()
            if client is None:
                logger.warning(f"Redis client unavailable for SET key {key}")
                return
            client.set(key, _serialize(value), ex=ex)
        except Exception as e:
            logger.warning(f"Redis SET failed for key {key}: {e}")

    def delete(self, key: str) -> None:
        try:
            client = self._get_client()
            if client is None:
                logger.warning(f"Redis client unavailable for DELETE key {key}")
                return
            client.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE failed for key {key}: {e}")


cache_service = CacheService()


def cache_response(
    key_generator: Callable[..., str],
    ttl: int | None = None,
    revive: type[T] | Callable[[Any], T] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def async_wrapper(*args, **kwargs) -> Any:
            key = key_generator(*args, **kwargs)
            cached_value = cache_service.get(key, revive=revive)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            cache_service.set(key, result, ex=ttl)
            return result

        return async_wrapper

    return decorator
