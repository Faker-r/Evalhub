"""Unit tests for BenchmarkService with mocked repository."""

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from api.benchmarks.service import BenchmarkService


@pytest.fixture
def service():
    mock_session = AsyncMock()
    svc = BenchmarkService(mock_session)
    svc.repository = AsyncMock()
    return svc


def _mock_benchmark(bid=1, dataset_name="test_bench", tasks_rel=None):
    from datetime import datetime

    b = MagicMock()
    b.id = bid
    b.dataset_name = dataset_name
    b.hf_repo = "test/repo"
    b.tasks = ["task1"]
    b.description = "A test benchmark"
    b.author = "tester"
    b.downloads = 100
    b.tags = ["test"]
    b.repo_type = "dataset"
    b.created_at_hf = None
    b.private = False
    b.gated = False
    b.files = None
    b.created_at = datetime(2025, 1, 1)
    b.updated_at = datetime(2025, 1, 1)
    b.default_dataset_size = None
    b.default_estimated_input_tokens = None
    b.tasks_rel = tasks_rel or []
    return b


def _mock_task(task_name="task1", dataset_size=100, estimated_input_tokens=50000):
    from datetime import datetime

    t = MagicMock()
    t.id = 1
    t.benchmark_id = 1
    t.task_name = task_name
    t.hf_subset = None
    t.evaluation_splits = None
    t.dataset_size = dataset_size
    t.estimated_input_tokens = estimated_input_tokens
    t.created_at = datetime(2025, 1, 1)
    t.updated_at = datetime(2025, 1, 1)
    return t


class TestGetAllBenchmarks:
    async def test_returns_paginated(self, service):
        benchmarks = [_mock_benchmark(1), _mock_benchmark(2)]
        service.repository.get_all.return_value = (benchmarks, 2)

        result = await service.get_all_benchmarks(page=1, page_size=10)

        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1
        assert len(result.benchmarks) == 2

    async def test_empty_results(self, service):
        service.repository.get_all.return_value = ([], 0)

        result = await service.get_all_benchmarks()

        assert result.total == 0
        assert result.total_pages == 0
        assert result.benchmarks == []

    async def test_populates_default_task_info(self, service):
        task = _mock_task(dataset_size=500, estimated_input_tokens=100000)
        benchmark = _mock_benchmark(tasks_rel=[task])
        service.repository.get_all.return_value = ([benchmark], 1)

        result = await service.get_all_benchmarks()

        assert result.benchmarks[0].default_dataset_size == 500
        assert result.benchmarks[0].default_estimated_input_tokens == 100000

    async def test_pagination_calculation(self, service):
        service.repository.get_all.return_value = ([], 55)

        result = await service.get_all_benchmarks(page=2, page_size=10)
        assert result.total_pages == 6


class TestGetBenchmark:
    async def test_returns_benchmark(self, service):
        benchmark = _mock_benchmark()
        service.repository.get_by_id.return_value = benchmark

        result = await service.get_benchmark(1)
        assert result.dataset_name == "test_bench"


class TestGetBenchmarkByDatasetName:
    async def test_found(self, service):
        benchmark = _mock_benchmark(dataset_name="gsm8k")
        service.repository.get_by_dataset_name.return_value = benchmark

        result = await service.get_benchmark_by_dataset_name("gsm8k")
        assert result is not None
        assert result.dataset_name == "gsm8k"

    async def test_not_found(self, service):
        service.repository.get_by_dataset_name.return_value = None

        result = await service.get_benchmark_by_dataset_name("nonexistent")
        assert result is None


class TestGetTaskDetails:
    async def test_with_details(self, service):
        service.repository.get_task_details.return_value = {"key": "value"}

        result = await service.get_task_details("gsm8k")
        assert result.task_name == "gsm8k"
        assert result.task_details_nested_dict == {"key": "value"}

    async def test_without_details(self, service):
        service.repository.get_task_details.return_value = None

        result = await service.get_task_details("unknown_task")
        assert result.task_name == "unknown_task"


class TestGetBenchmarkTasks:
    async def test_returns_tasks(self, service):
        tasks = [_mock_task("task1"), _mock_task("task2")]
        service.repository.get_tasks_by_benchmark_id.return_value = tasks

        result = await service.get_benchmark_tasks(1)
        assert len(result.tasks) == 2
