"""Unit tests for DatasetRepository."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from api.core.exceptions import NotFoundException
from api.datasets.repository import DatasetRepository


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repo(session):
    return DatasetRepository(session)


def _mock_result(scalar_value=None, scalars_value=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar_value
    if scalars_value is not None:
        r.scalars.return_value.all.return_value = scalars_value
    return r


class TestCreateFromFile:
    async def test_creates_dataset(self, repo, session):
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        dataset = await repo.create_from_file("ds1", "general", 10)
        session.add.assert_called_once()
        session.commit.assert_called_once()
        assert dataset.name == "ds1"
        assert dataset.sample_count == 10


class TestGetAll:
    async def test_returns_all(self, repo, session):
        datasets = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_result(scalars_value=datasets)

        result = await repo.get_all()
        assert len(result) == 2


class TestGetById:
    async def test_found(self, repo, session):
        ds = MagicMock(id=1)
        session.execute.return_value = _mock_result(scalar_value=ds)

        result = await repo.get_by_id(1)
        assert result.id == 1

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await repo.get_by_id(999)


class TestGetByName:
    async def test_found(self, repo, session):
        ds = MagicMock()
        ds.name = "ds1"
        session.execute.return_value = _mock_result(scalar_value=ds)

        result = await repo.get_by_name("ds1")
        assert result.name == "ds1"

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        result = await repo.get_by_name("nonexistent")
        assert result is None
