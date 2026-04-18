"""Unit tests for LeaderboardService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.leaderboard.service import LeaderboardService


@pytest.fixture
def service():
    mock_session = AsyncMock()
    svc = LeaderboardService(mock_session)
    svc.repository = AsyncMock()
    return svc


def _make_trace(
    trace_id,
    dataset_name,
    summary,
    completion_model="gpt-4o",
    model_provider="openai",
    judge_model="gpt-4o",
):
    t = MagicMock()
    t.id = trace_id
    t.dataset_name = dataset_name
    t.summary = summary
    t.completion_model = completion_model
    t.model_provider = model_provider
    t.judge_model = judge_model
    t.created_at = datetime(2025, 1, 1)
    return t


class TestBuildEntry:
    def test_valid_scores(self, service):
        trace = _make_trace(
            1,
            "ds1",
            {"scores": {"quality": {"mean": 4.0, "std": 0.5, "failed": 1}}},
        )
        entry = service._build_entry(trace)
        assert entry is not None
        assert entry.trace_id == 1
        assert entry.dataset_name == "ds1"
        assert len(entry.scores) == 1
        assert entry.scores[0].metric_name == "quality"
        assert entry.scores[0].mean == 4.0
        assert entry.scores[0].failed == 1
        assert entry.total_failures == 1

    def test_missing_summary_returns_none(self, service):
        trace = _make_trace(2, "ds", None)
        assert service._build_entry(trace) is None

    def test_summary_without_scores_returns_none(self, service):
        trace = _make_trace(3, "ds", {"other": "data"})
        assert service._build_entry(trace) is None

    def test_empty_metric_scores_returns_none(self, service):
        trace = _make_trace(4, "ds", {"scores": {}})
        assert service._build_entry(trace) is None


class TestGetLeaderboard:
    async def test_empty_traces(self, service):
        service.repository.get_all_leaderboard_traces.return_value = []

        result = await service.get_leaderboard()
        assert result.datasets == []

    async def test_one_dataset_with_entry(self, service):
        trace = _make_trace(
            10,
            "my_ds",
            {"scores": {"m1": {"mean": 1.0, "std": 0.0, "failed": 0}}},
        )
        service.repository.get_all_leaderboard_traces.return_value = [trace]
        ds = MagicMock()
        ds.sample_count = 42
        service.repository.get_dataset_by_name.return_value = ds

        result = await service.get_leaderboard()
        assert len(result.datasets) == 1
        lb = result.datasets[0]
        assert lb.dataset_name == "my_ds"
        assert lb.sample_count == 42
        assert len(lb.entries) == 1
        assert lb.entries[0].trace_id == 10
