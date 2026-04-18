"""Unit tests for ModelsAndProvidersService with mocked DB session."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.models_and_providers.schemas import (
    ModelCreate,
    ModelUpdate,
    ProviderCreate,
    ProviderUpdate,
)
from api.models_and_providers.service import ModelsAndProvidersService

PID1 = "11111111-1111-1111-1111-111111111111"
PID2 = "22222222-2222-2222-2222-222222222222"
MID1 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PID_MISSING = "99999999-9999-9999-9999-999999999999"


def _mock_provider(
    pid=PID1, name="OpenAI", slug="openai", base_url="https://api.openai.com"
):
    p = MagicMock()
    p.id = pid
    p.name = name
    p.slug = slug
    p.base_url = base_url
    return p


def _mock_model(
    mid=MID1,
    display_name="GPT-4o",
    developer="OpenAI",
    api_name="gpt-4o",
    providers=None,
):
    m = MagicMock()
    m.id = mid
    m.display_name = display_name
    m.developer = developer
    m.api_name = api_name
    m.providers = providers or []
    return m


def _mock_execute_result(scalar_value=None, scalars_list=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    if scalars_list is not None:
        result.scalars.return_value.all.return_value = scalars_list
    return result


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return ModelsAndProvidersService(session)


# ==================== Provider Tests ====================


class TestCreateProvider:
    async def test_success(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)
        session.add = MagicMock()

        async def fake_refresh(obj, *args, **kwargs):
            obj.id = PID1

        session.refresh = fake_refresh

        data = ProviderCreate(
            name="OpenAI", slug="openai", base_url="https://api.openai.com"
        )

        result = await service.create_provider(data)
        assert result.name == "OpenAI"
        assert result.id == PID1
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_duplicate_raises(self, service, session):
        existing = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=existing)

        data = ProviderCreate(
            name="OpenAI", slug="openai", base_url="https://api.openai.com"
        )

        with pytest.raises(AlreadyExistsException, match="already exists"):
            await service.create_provider(data)


class TestGetProvider:
    async def test_found(self, service, session):
        provider = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=provider)

        result = await service.get_provider(PID1)
        assert result.name == "OpenAI"

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.get_provider(PID_MISSING)


class TestGetProviderByName:
    async def test_found(self, service, session):
        provider = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=provider)

        result = await service.get_provider_by_name("OpenAI")
        assert result.name == "OpenAI"

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.get_provider_by_name("Unknown")


class TestListProviders:
    async def test_returns_paginated(self, service, session):
        providers = [_mock_provider(PID1, "OpenAI"), _mock_provider(PID2, "Anthropic")]
        session.execute.side_effect = [
            _mock_execute_result(scalars_list=providers),
            _mock_execute_result(scalars_list=providers),
        ]

        result = await service.list_providers(page=1, page_size=10)
        assert result.total == 2
        assert result.page == 1


class TestUpdateProvider:
    async def test_success(self, service, session):
        provider = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=provider)
        session.refresh = AsyncMock()

        data = ProviderUpdate(base_url="https://new-url.com")
        result = await service.update_provider(PID1, data)
        session.commit.assert_called_once()

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.update_provider(PID_MISSING, ProviderUpdate())

    async def test_name_conflict(self, service, session):
        provider = _mock_provider(PID1, "OpenAI")
        existing = _mock_provider(PID2, "NewName")

        session.execute.side_effect = [
            _mock_execute_result(scalar_value=provider),
            _mock_execute_result(scalar_value=existing),
        ]

        with pytest.raises(AlreadyExistsException):
            await service.update_provider(PID1, ProviderUpdate(name="NewName"))


class TestDeleteProvider:
    async def test_success(self, service, session):
        provider = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=provider)

        await service.delete_provider(PID1)
        session.delete.assert_called_once_with(provider)
        session.commit.assert_called_once()

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.delete_provider(PID_MISSING)


# ==================== Model Tests ====================


class TestCreateModel:
    async def test_success(self, service, session):
        provider = _mock_provider()
        session.execute.return_value = _mock_execute_result(scalar_value=provider)
        session.add = MagicMock()

        async def fake_refresh(obj, *args, **kwargs):
            obj.id = MID1
            if not hasattr(obj, "providers") or not isinstance(obj.providers, list):
                obj.providers = [provider]

        session.refresh = fake_refresh

        data = ModelCreate(
            display_name="GPT-4o",
            developer="OpenAI",
            api_name="gpt-4o",
            provider_ids=[PID1],
        )

        result = await service.create_model(data)
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_provider_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        data = ModelCreate(
            display_name="GPT-4o",
            developer="OpenAI",
            api_name="gpt-4o",
            provider_ids=[PID_MISSING],
        )

        with pytest.raises(NotFoundException, match="Provider"):
            await service.create_model(data)


class TestGetModel:
    async def test_found(self, service, session):
        model = _mock_model(providers=[_mock_provider()])
        session.execute.return_value = _mock_execute_result(scalar_value=model)

        result = await service.get_model(MID1)
        assert result.display_name == "GPT-4o"

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.get_model(PID_MISSING)


class TestListModels:
    async def test_returns_paginated(self, service, session):
        models = [_mock_model(MID1, providers=[_mock_provider()])]
        session.execute.side_effect = [
            _mock_execute_result(scalars_list=models),
            _mock_execute_result(scalars_list=models),
        ]

        result = await service.list_models(page=1, page_size=10)
        assert result.total == 1
        assert result.page == 1

    async def test_filter_by_provider(self, service, session):
        models = [_mock_model(MID1, providers=[_mock_provider()])]
        session.execute.side_effect = [
            _mock_execute_result(scalars_list=models),
            _mock_execute_result(scalars_list=models),
        ]

        result = await service.list_models(provider_id=PID1)
        assert result.total == 1


class TestUpdateModel:
    async def test_success(self, service, session):
        model = _mock_model(providers=[_mock_provider()])
        session.execute.return_value = _mock_execute_result(scalar_value=model)
        session.refresh = AsyncMock()

        data = ModelUpdate(display_name="GPT-4o-Updated")
        result = await service.update_model(MID1, data)
        session.commit.assert_called_once()

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.update_model(PID_MISSING, ModelUpdate())

    async def test_update_providers(self, service, session):
        model = _mock_model(providers=[_mock_provider()])
        new_provider = _mock_provider(PID2, "Anthropic")

        session.execute.side_effect = [
            _mock_execute_result(scalar_value=model),
            _mock_execute_result(scalar_value=new_provider),
        ]
        session.refresh = AsyncMock()

        data = ModelUpdate(provider_ids=[PID2])
        await service.update_model(MID1, data)
        assert model.providers == [new_provider]

    async def test_update_provider_not_found(self, service, session):
        model = _mock_model(providers=[_mock_provider()])

        session.execute.side_effect = [
            _mock_execute_result(scalar_value=model),
            _mock_execute_result(scalar_value=None),
        ]

        data = ModelUpdate(provider_ids=[PID_MISSING])
        with pytest.raises(NotFoundException, match="Provider"):
            await service.update_model(MID1, data)


class TestDeleteModel:
    async def test_success(self, service, session):
        model = _mock_model()
        session.execute.return_value = _mock_execute_result(scalar_value=model)

        await service.delete_model(MID1)
        session.delete.assert_called_once_with(model)
        session.commit.assert_called_once()

    async def test_not_found(self, service, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await service.delete_model(PID_MISSING)
