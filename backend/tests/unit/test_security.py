"""Unit tests for JWT security module."""

from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

from api.core.security import CurrentUser, get_current_user, get_jwks_client


class TestCurrentUser:
    def test_creation(self):
        user = CurrentUser(id="abc-123", email="test@test.com")
        assert user.id == "abc-123"
        assert user.email == "test@test.com"


class TestGetJwksClient:
    @patch("api.core.security.settings")
    @patch("api.core.security.PyJWKClient")
    def test_returns_jwks_client(self, mock_pyjwk, mock_settings):
        get_jwks_client.cache_clear()
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        client = get_jwks_client()
        mock_pyjwk.assert_called_once_with(
            "https://example.supabase.co/auth/v1/.well-known/jwks.json"
        )
        get_jwks_client.cache_clear()


class TestGetCurrentUser:
    @patch("api.core.security.get_jwks_client")
    @patch("api.core.security.jwt.decode")
    async def test_valid_token(self, mock_decode, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.return_value = {
            "sub": "user-uuid-123",
            "email": "test@evalhub.com",
        }

        creds = MagicMock()
        creds.credentials = "valid.jwt.token"

        user = await get_current_user(credentials=creds)

        assert user.id == "user-uuid-123"
        assert user.email == "test@evalhub.com"
        mock_decode.assert_called_once()

    @patch("api.core.security.get_jwks_client")
    @patch("api.core.security.jwt.decode")
    async def test_missing_sub_field(self, mock_decode, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.return_value = {"email": "test@evalhub.com"}

        creds = MagicMock()
        creds.credentials = "token.without.sub"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)
        assert exc_info.value.status_code == 401

    @patch("api.core.security.get_jwks_client")
    @patch("api.core.security.jwt.decode")
    async def test_missing_email_defaults_empty(self, mock_decode, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.return_value = {"sub": "user-123", "email": None}

        creds = MagicMock()
        creds.credentials = "token"

        user = await get_current_user(credentials=creds)
        assert user.email == ""

    @patch("api.core.security.get_jwks_client")
    @patch("api.core.security.jwt.decode")
    async def test_expired_token(self, mock_decode, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.side_effect = jwt.ExpiredSignatureError()

        creds = MagicMock()
        creds.credentials = "expired.token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @patch("api.core.security.get_jwks_client")
    @patch("api.core.security.jwt.decode")
    async def test_invalid_token(self, mock_decode, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_decode.side_effect = jwt.InvalidTokenError("bad token")

        creds = MagicMock()
        creds.credentials = "invalid.token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)
        assert exc_info.value.status_code == 401

    @patch("api.core.security.get_jwks_client")
    async def test_unexpected_error(self, mock_get_jwks):
        mock_jwks = MagicMock()
        mock_get_jwks.return_value = mock_jwks
        mock_jwks.get_signing_key_from_jwt.side_effect = Exception("network error")

        creds = MagicMock()
        creds.credentials = "some.token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)
        assert exc_info.value.status_code == 401
