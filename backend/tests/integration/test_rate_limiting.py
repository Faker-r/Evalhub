"""Integration tests for SlowAPI rate limiting (memory storage, no Redis)."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware

from api.core.ratelimiter import rate_limit_key


def _make_memory_limiter(application_limits: list[str]) -> Limiter:
    return Limiter(
        key_func=rate_limit_key,
        application_limits=application_limits,
        default_limits=[],
        storage_uri="memory://",
        strategy="fixed-window",
        swallow_errors=False,
    )


@pytest.fixture
def limited_app() -> FastAPI:
    """Minimal app: same middleware/handlers as Evalhub, one non-exempt route."""
    app = FastAPI()
    limiter = _make_memory_limiter(["3/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIASGIMiddleware)

    @app.get("/limited")
    async def limited():
        return {"ok": True}

    return app


def test_application_limit_returns_429_after_threshold(limited_app: FastAPI):
    with TestClient(limited_app) as client:
        assert client.get("/limited").status_code == 200
        assert client.get("/limited").status_code == 200
        assert client.get("/limited").status_code == 200
        r = client.get("/limited")
        assert r.status_code == 429
        body = r.json()
        assert "error" in body
        assert "Rate limit exceeded" in body["error"]


def test_exempt_route_not_counted_against_limit(limited_app: FastAPI):
    limiter = limited_app.state.limiter

    @limited_app.get("/health")
    @limiter.exempt
    async def health():
        return {"status": "ok"}

    with TestClient(limited_app) as client:
        for _ in range(10):
            assert client.get("/health").status_code == 200
        assert client.get("/limited").status_code == 200


def test_x_forwarded_for_splits_clients_when_behind_proxy(limited_app: FastAPI):
    with patch("api.core.ratelimiter.settings") as mock_settings:
        mock_settings.RATE_LIMIT_BEHIND_PROXY = True
        with TestClient(limited_app) as client:
            a = client.get(
                "/limited", headers={"X-Forwarded-For": "203.0.113.10"}
            )
            b = client.get(
                "/limited", headers={"X-Forwarded-For": "203.0.113.20"}
            )
            assert a.status_code == 200
            assert b.status_code == 200
