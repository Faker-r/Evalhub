"""Unit tests for GuidelineService with mocked repository."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from api.guidelines.service import GuidelineService


@pytest.fixture
def service():
    mock_session = AsyncMock()
    svc = GuidelineService(mock_session)
    svc.repository = AsyncMock()
    return svc


def _mock_guideline(gid=1, name="test_guideline"):
    g = MagicMock()
    g.id = gid
    g.name = name
    return g


class TestCreateGuideline:
    async def test_success(self, service):
        service.repository.get_by_name.return_value = None
        expected = _mock_guideline()
        service.repository.create.return_value = expected

        guideline_data = MagicMock()
        guideline_data.name = "new_guideline"

        result = await service.create_guideline(guideline_data, "user-uuid")
        assert result == expected
        service.repository.create.assert_called_once_with(guideline_data, "user-uuid")

    async def test_duplicate_name_raises_409(self, service):
        service.repository.get_by_name.return_value = _mock_guideline()

        guideline_data = MagicMock()
        guideline_data.name = "test_guideline"

        with pytest.raises(HTTPException) as exc_info:
            await service.create_guideline(guideline_data, "user-uuid")
        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail


class TestGetAllGuidelines:
    async def test_returns_all(self, service):
        guidelines = [_mock_guideline(1), _mock_guideline(2)]
        service.repository.get_all.return_value = guidelines

        result = await service.get_all_guidelines()
        assert len(result) == 2


class TestGetGuideline:
    async def test_returns_by_id(self, service):
        expected = _mock_guideline()
        service.repository.get_by_id.return_value = expected

        result = await service.get_guideline(1)
        assert result == expected


class TestGetGuidelineByName:
    async def test_found(self, service):
        expected = _mock_guideline(name="helpfulness")
        service.repository.get_by_name.return_value = expected

        result = await service.get_guideline_by_name("helpfulness")
        assert result == expected

    async def test_not_found_raises_404(self, service):
        service.repository.get_by_name.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await service.get_guideline_by_name("missing")
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
