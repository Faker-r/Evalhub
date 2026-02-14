import json
from typing import Any, Callable, TypeVar
import redis
from pydantic import BaseModel

from api.core.config import settings

T = TypeVar("T")


def _serialize(value: Any) -> str:
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return json.dumps(value)


def _deserialize(raw: str, revive: type[T] | Callable[[Any], T] | None = None) -> T | dict[str, Any]:
    data = json.loads(raw)
    if revive is None:
        return data
    if isinstance(revive, type) and issubclass(revive, BaseModel):
        return revive.model_validate(data)
    return revive(data)


class CacheService:
    def __init__(self):
        self._redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def get(self, key: str, revive: type[T] | Callable[[Any], T] | None = None) -> T | dict[str, Any] | None:
        raw = self._redis_client.get(key)
        if raw is None:
            return None
        return _deserialize(raw, revive)

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self._redis_client.set(key, _serialize(value), ex=ex)

    def delete(self, key: str) -> None:
        self._redis_client.delete(key)


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
