"""Unit tests for UserService with mocked S3 and DB session."""

from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

from api.core.exceptions import NotFoundException
from api.users.schemas import ApiKeyCreate, ApiKeyResponse
from api.users.service import UserService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    with patch("api.users.service.S3Storage") as MockS3:
        mock_s3 = MagicMock()
        MockS3.return_value = mock_s3
        svc = UserService(session=mock_session)
        svc.s3 = mock_s3
        yield svc


def _mock_provider(provider_id=1, name="OpenAI", slug="openai"):
    provider = MagicMock()
    provider.id = provider_id
    provider.name = name
    provider.slug = slug
    return provider


def _mock_execute_result(scalar_value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    return result


class TestCreateApiKey:
    async def test_success(self, service, mock_session):
        provider = _mock_provider()
        mock_session.execute.return_value = _mock_execute_result(provider)

        api_key_data = ApiKeyCreate(provider_id=1, api_key="sk-abc123")
        result = await service.create_api_key("user-uuid", api_key_data)

        assert isinstance(result, ApiKeyResponse)
        assert result.provider_id == 1
        assert result.provider_name == "OpenAI"
        service.s3.upload_api_key.assert_called_once_with(
            "user-uuid", "openai", "sk-abc123"
        )

    async def test_provider_not_found(self, service, mock_session):
        mock_session.execute.return_value = _mock_execute_result(None)

        api_key_data = ApiKeyCreate(provider_id=999, api_key="sk-abc")
        with pytest.raises(NotFoundException, match="Provider"):
            await service.create_api_key("user-uuid", api_key_data)

    async def test_no_session_raises(self):
        with patch("api.users.service.S3Storage"):
            svc = UserService(session=None)
        api_key_data = ApiKeyCreate(provider_id=1, api_key="sk-abc")
        with pytest.raises(ValueError, match="session required"):
            await svc.create_api_key("user", api_key_data)


class TestGetApiKey:
    async def test_success(self, service, mock_session):
        provider = _mock_provider()
        mock_session.execute.return_value = _mock_execute_result(provider)
        service.s3.download_api_key.return_value = "sk-secret"

        result = await service.get_api_key("user-uuid", 1)
        assert result == "sk-secret"

    async def test_provider_not_found(self, service, mock_session):
        mock_session.execute.return_value = _mock_execute_result(None)

        with pytest.raises(NotFoundException):
            await service.get_api_key("user-uuid", 999)

    async def test_api_key_not_found(self, service, mock_session):
        provider = _mock_provider()
        mock_session.execute.return_value = _mock_execute_result(provider)
        service.s3.download_api_key.side_effect = FileNotFoundError()

        with pytest.raises(NotFoundException, match="API key not found"):
            await service.get_api_key("user-uuid", 1)

    async def test_no_session_raises(self):
        with patch("api.users.service.S3Storage"):
            svc = UserService(session=None)
        with pytest.raises(ValueError, match="session required"):
            await svc.get_api_key("user", 1)


class TestListApiKeys:
    async def test_returns_provider_list(self, service, mock_session):
        service.s3.list_user_api_keys.return_value = ["openai", "anthropic"]

        provider_openai = _mock_provider(1, "OpenAI", "openai")
        provider_anthropic = _mock_provider(2, "Anthropic", "anthropic")

        mock_session.execute.side_effect = [
            _mock_execute_result(provider_openai),
            _mock_execute_result(provider_anthropic),
        ]

        result = await service.list_api_keys("user-uuid")
        assert len(result) == 2
        assert result[0].provider_name == "OpenAI"
        assert result[1].provider_name == "Anthropic"

    async def test_skips_unknown_providers(self, service, mock_session):
        service.s3.list_user_api_keys.return_value = ["openai", "unknown"]

        provider_openai = _mock_provider(1, "OpenAI", "openai")

        mock_session.execute.side_effect = [
            _mock_execute_result(provider_openai),
            _mock_execute_result(None),
        ]

        result = await service.list_api_keys("user-uuid")
        assert len(result) == 1
        assert result[0].provider_name == "OpenAI"

    async def test_empty_list(self, service, mock_session):
        service.s3.list_user_api_keys.return_value = []
        result = await service.list_api_keys("user-uuid")
        assert result == []

    async def test_no_session_raises(self):
        with patch("api.users.service.S3Storage"):
            svc = UserService(session=None)
        with pytest.raises(ValueError, match="session required"):
            await svc.list_api_keys("user")


class TestDeleteApiKey:
    async def test_success(self, service, mock_session):
        provider = _mock_provider()
        mock_session.execute.return_value = _mock_execute_result(provider)
        service.s3.api_key_exists.return_value = True

        await service.delete_api_key("user-uuid", 1)
        service.s3.delete_api_key.assert_called_once_with("user-uuid", "openai")

    async def test_provider_not_found(self, service, mock_session):
        mock_session.execute.return_value = _mock_execute_result(None)

        with pytest.raises(NotFoundException):
            await service.delete_api_key("user-uuid", 999)

    async def test_api_key_not_found(self, service, mock_session):
        provider = _mock_provider()
        mock_session.execute.return_value = _mock_execute_result(provider)
        service.s3.api_key_exists.return_value = False

        with pytest.raises(NotFoundException, match="API key not found"):
            await service.delete_api_key("user-uuid", 1)

    async def test_no_session_raises(self):
        with patch("api.users.service.S3Storage"):
            svc = UserService(session=None)
        with pytest.raises(ValueError, match="session required"):
            await svc.delete_api_key("user", 1)
