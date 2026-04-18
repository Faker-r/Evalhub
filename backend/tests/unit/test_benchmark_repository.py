"""Unit tests for BenchmarkRepository."""

import functools
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.benchmarks.repository import BenchmarkRepository
from api.core.exceptions import NotFoundException


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repo(session):
    return BenchmarkRepository(session)


def _mock_result(scalar_value=None, scalars_value=None, scalar_val=None):
    r = MagicMock()
    r.scalar_one_or_none.return_value = scalar_value
    if scalars_value is not None:
        r.scalars.return_value.all.return_value = scalars_value
    if scalar_val is not None:
        r.scalar.return_value = scalar_val
    return r


class TestCreate:
    async def test_creates_benchmark(self, repo, session):
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        data = {"dataset_name": "test_bench", "hf_repo": "test/repo", "tasks": ["t1"]}
        benchmark = await repo.create(data)
        session.add.assert_called_once()
        session.commit.assert_called_once()
        assert benchmark.dataset_name == "test_bench"


class TestUpdate:
    async def test_updates_benchmark(self, repo, session):
        benchmark = MagicMock(id=1, dataset_name="old_name")
        session.execute.return_value = _mock_result(scalar_value=benchmark)
        session.refresh = AsyncMock()

        result = await repo.update(1, {"dataset_name": "new_name"})
        assert benchmark.dataset_name == "new_name"
        session.commit.assert_called()


class TestGetById:
    async def test_found(self, repo, session):
        b = MagicMock(id=1)
        session.execute.return_value = _mock_result(scalar_value=b)

        result = await repo.get_by_id(1)
        assert result.id == 1

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await repo.get_by_id(999)


class TestGetByDatasetName:
    async def test_found(self, repo, session):
        b = MagicMock(dataset_name="ds")
        session.execute.return_value = _mock_result(scalar_value=b)

        result = await repo.get_by_dataset_name("ds")
        assert result.dataset_name == "ds"

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)

        result = await repo.get_by_dataset_name("nonexistent")
        assert result is None


class TestUpsert:
    async def test_creates_new(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        result = await repo.upsert("new_ds", {"hf_repo": "test/repo"})
        session.add.assert_called_once()

    async def test_updates_existing(self, repo, session):
        existing = MagicMock(id=1, dataset_name="ds")
        # First call returns existing, second call returns existing for get_by_id in update
        session.execute.side_effect = [
            _mock_result(scalar_value=existing),
            _mock_result(scalar_value=existing),
        ]
        session.refresh = AsyncMock()

        result = await repo.upsert("ds", {"hf_repo": "updated/repo"})
        assert existing.hf_repo == "updated/repo"


class TestGetAll:
    async def test_returns_paginated(self, repo, session):
        benchmarks = [MagicMock(id=1), MagicMock(id=2)]
        # Two executes: count then main query
        session.execute.side_effect = [
            _mock_result(scalar_val=2),
            _mock_result(scalars_value=benchmarks),
        ]

        result, total = await repo.get_all(page=1, page_size=10)
        assert total == 2
        assert len(result) == 2

    async def test_sort_asc(self, repo, session):
        session.execute.side_effect = [
            _mock_result(scalar_val=0),
            _mock_result(scalars_value=[]),
        ]

        result, total = await repo.get_all(sort_order="asc")
        assert total == 0

    async def test_with_filters(self, repo, session):
        session.execute.side_effect = [
            _mock_result(scalar_val=1),
            _mock_result(scalars_value=[MagicMock()]),
        ]

        result, total = await repo.get_all(
            tag_filter=["nlp"],
            author_filter="test_author",
            search_query="mmlu",
        )
        assert total == 1

    @patch("api.benchmarks.repository.normalize_language_code", return_value="en")
    async def test_search_with_language_normalization(
        self, mock_normalize, repo, session
    ):
        session.execute.side_effect = [
            _mock_result(scalar_val=1),
            _mock_result(scalars_value=[MagicMock()]),
        ]

        result, total = await repo.get_all(search_query="english")
        assert total == 1
        mock_normalize.assert_called()


class TestGenerateTaskDetailsDict:
    def test_converts_partial(self, repo):
        task_obj = MagicMock()

        def my_func(x):
            return x

        from dataclasses import asdict
        from unittest.mock import patch

        with patch("api.benchmarks.repository.asdict") as mock_asdict:
            mock_asdict.return_value = {
                "name": "task1",
                "fn": functools.partial(my_func, 1),
                "nested": {"inner": functools.partial(my_func, 2)},
                "list_val": [functools.partial(my_func, 3)],
            }

            result = repo._generate_task_details_dict(task_obj)
            assert "partial(my_func, ...)" in result["fn"]
            assert "partial(my_func, ...)" in result["nested"]["inner"]


class TestGetTaskDetails:
    @patch("api.benchmarks.repository.Registry")
    async def test_found(self, MockRegistry, repo):
        mock_config = MagicMock()
        mock_task = MagicMock()
        mock_task.config = mock_config
        registry_instance = MockRegistry.return_value
        registry_instance.load_tasks.return_value = {"task1": mock_task}

        with patch.object(
            repo, "_generate_task_details_dict", return_value={"name": "task1"}
        ):
            result = await repo.get_task_details("task1")
        assert result == {"name": "task1"}

    @patch("api.benchmarks.repository.Registry")
    async def test_not_found(self, MockRegistry, repo):
        registry_instance = MockRegistry.return_value
        registry_instance.load_tasks.return_value = {}

        result = await repo.get_task_details("nonexistent")
        assert result is None

    @patch("api.benchmarks.repository.Registry")
    async def test_fallback_with_pipe(self, MockRegistry, repo):
        mock_task = MagicMock()
        registry_instance = MockRegistry.return_value
        registry_instance.load_tasks.return_value = {"task1|0": mock_task}

        with patch.object(
            repo, "_generate_task_details_dict", return_value={"name": "task1|0"}
        ):
            result = await repo.get_task_details("task1")
        assert result is not None


class TestUpsertTask:
    async def test_creates_new_task(self, repo, session):
        session.execute.return_value = _mock_result(scalar_value=None)
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        data = {"task_name": "task1", "dataset_size": 100}
        result = await repo.upsert_task(1, data)
        session.add.assert_called_once()

    async def test_updates_existing_task(self, repo, session):
        existing = MagicMock(id=1, task_name="task1")
        session.execute.return_value = _mock_result(scalar_value=existing)
        session.refresh = AsyncMock()

        data = {"task_name": "task1", "dataset_size": 200}
        result = await repo.upsert_task(1, data)
        assert existing.dataset_size == 200


class TestGetTasksByBenchmarkId:
    async def test_returns_tasks(self, repo, session):
        tasks = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_result(scalars_value=tasks)

        result = await repo.get_tasks_by_benchmark_id(1)
        assert len(result) == 2
