import json
import logging
from typing import Any, Callable, TypeVar
import redis
from pydantic import BaseModel

from api.core.config import settings

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
    def __init__(self):
        self._redis_client = None

    def _get_client(self):
        if self._redis_client is None:
            logger.info(f"Initializing Redis client with URL: {settings.REDIS_URL}")
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                    retry_on_timeout=True,
                    ssl_cert_reqs=None,
                )
                logger.info("Redis client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Redis client: {e}")
                raise
        return self._redis_client

    def get(
        self, key: str, revive: type[T] | Callable[[Any], T] | None = None
    ) -> T | dict[str, Any] | None:
        try:
            logger.info(f"Redis GET: {key}")
            raw = self._get_client().get(key)
            if raw is None:
                logger.info(f"Redis GET {key}: cache miss")
                return None
            logger.info(f"Redis GET {key}: cache hit")
            return _deserialize(raw, revive)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Redis GET failed for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        try:
            logger.info(f"Redis SET: {key} (ttl={ex})")
            self._get_client().set(key, _serialize(value), ex=ex)
            logger.info(f"Redis SET {key}: success")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Redis SET failed for key {key}: {e}")

    def delete(self, key: str) -> None:
        try:
            logger.info(f"Redis DELETE: {key}")
            self._get_client().delete(key)
            logger.info(f"Redis DELETE {key}: success")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
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
