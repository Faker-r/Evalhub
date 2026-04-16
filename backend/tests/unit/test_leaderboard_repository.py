"""Unit tests for LeaderboardRepository."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from api.leaderboard.repository import LeaderboardRepository


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repo(session):
    return LeaderboardRepository(session)


def _mock_result(scalar_value=None, scalars_value=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar_value
    if scalars_value is not None:
        r.scalars.return_value.all.return_value = scalars_value
    return r


class TestGetCompletedTracesByDataset:
    async def test_returns_traces(self, repo, session):
        traces = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_result(scalars_value=traces)

        result = await repo.get_completed_traces_by_dataset("ds1")
        assert len(result) == 2


class TestGetGuidelinesByNames:
    async def test_empty_names(self, repo, session):
        result = await repo.get_guidelines_by_names([])
        assert result == {}

    async def test_returns_dict(self, repo, session):
        g1 = MagicMock()
        g1.name = "g1"
        g2 = MagicMock()
        g2.name = "g2"
        session.execute.return_value = _mock_result(scalars_value=[g1, g2])

        result = await repo.get_guidelines_by_names(["g1", "g2"])
        assert "g1" in result
        assert "g2" in result


class TestGetDatasetByName:
    async def test_found(self, repo, session):
        ds = MagicMock()
        ds.name = "ds1"
        session.execute.return_value = _mock_result(scalar_value=ds)

        result = await repo.get_dataset_by_name("ds1")
        assert result.name == "ds1"

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        result = await repo.get_dataset_by_name("nonexistent")
        assert result is None
