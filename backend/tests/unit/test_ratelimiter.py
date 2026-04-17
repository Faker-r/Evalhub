"""Unit tests for rate limit key resolution."""

from unittest.mock import MagicMock, patch

from api.core.ratelimiter import rate_limit_key


def _make_request(
    *,
    x_forwarded_for: str | None = None,
    client_host: str | None = "192.0.2.1",
) -> MagicMock:
    req = MagicMock()
    req.headers = MagicMock()
    req.headers.get = MagicMock(
        return_value=x_forwarded_for if x_forwarded_for is not None else None
    )
    if client_host is None:
        req.client = None
    else:
        req.client = MagicMock()
        req.client.host = client_host
    return req


def test_rate_limit_key_uses_client_host_when_no_proxy_header():
    req = _make_request(client_host="10.0.0.5")
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = False
        assert rate_limit_key(req) == "10.0.0.5"


def test_rate_limit_key_ignores_x_forwarded_for_when_not_behind_proxy():
    req = _make_request(x_forwarded_for="203.0.113.9, 10.0.0.1", client_host="10.0.0.5")
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = False
        assert rate_limit_key(req) == "10.0.0.5"


def test_rate_limit_key_uses_first_x_forwarded_for_when_behind_proxy():
    req = _make_request(x_forwarded_for="203.0.113.9, 10.0.0.1", client_host="10.0.0.5")
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = True
        assert rate_limit_key(req) == "203.0.113.9"


def test_rate_limit_key_strips_whitespace_for_forwarded_for():
    req = _make_request(
        x_forwarded_for="  203.0.113.9  , 10.0.0.1", client_host="10.0.0.5"
    )
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = True
        assert rate_limit_key(req) == "203.0.113.9"


def test_rate_limit_key_falls_back_to_client_when_behind_proxy_but_no_header():
    req = _make_request(x_forwarded_for=None, client_host="10.0.0.5")
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = True
        assert rate_limit_key(req) == "10.0.0.5"


def test_rate_limit_key_unknown_when_no_client():
    req = _make_request(client_host=None)
    with patch("api.core.ratelimiter.settings") as s:
        s.RATE_LIMIT_BEHIND_PROXY = False
        assert rate_limit_key(req) == "unknown"
