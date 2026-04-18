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


class TestGetAllLeaderboardTraces:
    async def test_returns_traces(self, repo, session):
        traces = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_result(scalars_value=traces)

        result = await repo.get_all_leaderboard_traces()
        assert len(result) == 2


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
