"""Unit tests for AuthService with mocked Supabase client."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from api.auth.schemas import AuthResponse, LoginData, RefreshTokenRequest, UserCreate
from api.auth.service import AuthService
from api.core.exceptions import BadRequestException, UnauthorizedException


@pytest.fixture
def mock_supabase():
    with patch("api.auth.service.get_supabase_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


@pytest.fixture
def service(mock_supabase):
    return AuthService()


def _mock_user(user_id="user-uuid", email="test@test.com"):
    user = MagicMock()
    user.id = user_id
    user.email = email
    return user


def _mock_session(access_token="access-tok", refresh_token="refresh-tok", expires_in=3600):
    session = MagicMock()
    session.access_token = access_token
    session.refresh_token = refresh_token
    session.expires_in = expires_in
    return session


class TestRegister:
    async def test_success(self, service, mock_supabase):
        user = _mock_user()
        session = _mock_session()
        response = MagicMock()
        response.user = user
        response.session = session
        mock_supabase.auth.sign_up.return_value = response

        result = await service.register(
            UserCreate(email="test@test.com", password="pw123")
        )
        assert isinstance(result, AuthResponse)
        assert result.access_token == "access-tok"
        assert result.user_id == "user-uuid"

    async def test_user_none_raises(self, service, mock_supabase):
        response = MagicMock()
        response.user = None
        response.session = None
        mock_supabase.auth.sign_up.return_value = response

        with pytest.raises(BadRequestException, match="Registration failed"):
            await service.register(
                UserCreate(email="test@test.com", password="pw123")
            )

    async def test_email_confirmation_required(self, service, mock_supabase):
        user = _mock_user()
        response = MagicMock()
        response.user = user
        response.session = None
        mock_supabase.auth.sign_up.return_value = response

        with pytest.raises(BadRequestException, match="check your email"):
            await service.register(
                UserCreate(email="test@test.com", password="pw123")
            )

    async def test_auth_api_error(self, service, mock_supabase):
        from api.auth.service import AuthApiError

        mock_supabase.auth.sign_up.side_effect = AuthApiError("User already exists")

        with pytest.raises(BadRequestException):
            await service.register(
                UserCreate(email="test@test.com", password="pw123")
            )

    async def test_expires_in_default(self, service, mock_supabase):
        user = _mock_user()
        session = _mock_session()
        session.expires_in = None
        response = MagicMock()
        response.user = user
        response.session = session
        mock_supabase.auth.sign_up.return_value = response

        result = await service.register(
            UserCreate(email="test@test.com", password="pw123")
        )
        assert result.expires_in == 3600


class TestLogin:
    async def test_success(self, service, mock_supabase):
        user = _mock_user()
        session = _mock_session()
        response = MagicMock()
        response.user = user
        response.session = session
        mock_supabase.auth.sign_in_with_password.return_value = response

        result = await service.login(
            LoginData(email="test@test.com", password="pw123")
        )
        assert isinstance(result, AuthResponse)
        assert result.access_token == "access-tok"

    async def test_user_none_raises(self, service, mock_supabase):
        response = MagicMock()
        response.user = None
        response.session = None
        mock_supabase.auth.sign_in_with_password.return_value = response

        with pytest.raises(UnauthorizedException):
            await service.login(
                LoginData(email="test@test.com", password="wrong")
            )

    async def test_session_none_raises(self, service, mock_supabase):
        response = MagicMock()
        response.user = _mock_user()
        response.session = None
        mock_supabase.auth.sign_in_with_password.return_value = response

        with pytest.raises(UnauthorizedException):
            await service.login(
                LoginData(email="test@test.com", password="pw123")
            )

    async def test_auth_api_error(self, service, mock_supabase):
        from api.auth.service import AuthApiError

        mock_supabase.auth.sign_in_with_password.side_effect = AuthApiError(
            "Invalid credentials"
        )

        with pytest.raises(UnauthorizedException):
            await service.login(
                LoginData(email="test@test.com", password="wrong")
            )


class TestRefreshToken:
    async def test_success(self, service, mock_supabase):
        user = _mock_user()
        session = _mock_session(access_token="new-access", refresh_token="new-refresh")
        response = MagicMock()
        response.user = user
        response.session = session
        mock_supabase.auth.refresh_session.return_value = response

        result = await service.refresh_token(
            RefreshTokenRequest(refresh_token="old-refresh")
        )
        assert result.access_token == "new-access"
        assert result.refresh_token == "new-refresh"

    async def test_user_none_raises(self, service, mock_supabase):
        response = MagicMock()
        response.user = None
        response.session = None
        mock_supabase.auth.refresh_session.return_value = response

        with pytest.raises(UnauthorizedException):
            await service.refresh_token(
                RefreshTokenRequest(refresh_token="bad-token")
            )

    async def test_auth_api_error(self, service, mock_supabase):
        from api.auth.service import AuthApiError

        mock_supabase.auth.refresh_session.side_effect = AuthApiError("Expired")

        with pytest.raises(UnauthorizedException):
            await service.refresh_token(
                RefreshTokenRequest(refresh_token="expired")
            )


class TestLogout:
    async def test_success(self, service, mock_supabase):
        await service.logout("some-token")
        mock_supabase.auth.sign_out.assert_called_once()

    async def test_error_is_swallowed(self, service, mock_supabase):
        from api.auth.service import AuthApiError

        mock_supabase.auth.sign_out.side_effect = AuthApiError("Failed")
        await service.logout("some-token")
