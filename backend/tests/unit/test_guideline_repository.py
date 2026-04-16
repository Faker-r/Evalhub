"""Unit tests for GuidelineRepository."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from api.core.exceptions import NotFoundException
from api.guidelines.repository import GuidelineRepository
from api.guidelines.schemas import (
    BooleanScaleConfig,
    GuidelineCreate,
    GuidelineScoringScale,
)


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repo(session):
    return GuidelineRepository(session)


def _mock_result(scalar_value=None, scalars_value=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar_value
    if scalars_value is not None:
        r.scalars.return_value.all.return_value = scalars_value
    return r


class TestCreate:
    async def test_creates_guideline(self, repo, session):
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        data = GuidelineCreate(
            name="test_g",
            prompt="Is it good?",
            category="quality",
            scoring_scale=GuidelineScoringScale.BOOLEAN,
            scoring_scale_config=BooleanScaleConfig(),
        )

        guideline = await repo.create(data)
        session.add.assert_called_once()
        session.commit.assert_called_once()
        assert guideline.name == "test_g"
        assert guideline.scoring_scale == "boolean"


class TestGetAll:
    async def test_returns_all(self, repo, session):
        guidelines = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_result(scalars_value=guidelines)

        result = await repo.get_all()
        assert len(result) == 2


class TestGetById:
    async def test_found(self, repo, session):
        g = MagicMock(id=1)
        session.execute.return_value = _mock_result(scalar_value=g)

        result = await repo.get_by_id(1)
        assert result.id == 1

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await repo.get_by_id(999)


class TestGetByName:
    async def test_found(self, repo, session):
        g = MagicMock()
        g.name = "test_g"
        session.execute.return_value = _mock_result(scalar_value=g)

        result = await repo.get_by_name("test_g")
        assert result.name == "test_g"

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        result = await repo.get_by_name("nonexistent")
        assert result is None
