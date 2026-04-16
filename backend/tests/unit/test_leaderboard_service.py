"""Unit tests for LeaderboardService, focusing on pure logic methods."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.core.exceptions import NotFoundException
from api.leaderboard.service import LeaderboardService


@pytest.fixture
def service():
    mock_session = AsyncMock()
    svc = LeaderboardService(mock_session)
    svc.repository = AsyncMock()
    return svc


def _make_guideline(name, scoring_scale, scoring_scale_config=None):
    g = MagicMock()
    g.name = name
    g.scoring_scale = scoring_scale
    g.scoring_scale_config = scoring_scale_config or {}
    return g


def _make_trace(
    trace_id,
    guideline_names,
    summary,
    completion_model="gpt-4o",
    model_provider="openai",
    judge_model="gpt-4o",
):
    t = MagicMock()
    t.id = trace_id
    t.guideline_names = guideline_names
    t.summary = summary
    t.completion_model = completion_model
    t.model_provider = model_provider
    t.judge_model = judge_model
    t.created_at = datetime(2025, 1, 1)
    return t


class TestGetMaxScore:
    def test_boolean_scale(self, service):
        g = _make_guideline("g1", "boolean")
        assert service._get_max_score(g) == 1

    def test_numeric_scale(self, service):
        g = _make_guideline("g1", "numeric", {"max_value": 5})
        assert service._get_max_score(g) == 5

    def test_numeric_scale_default(self, service):
        g = _make_guideline("g1", "numeric", {})
        assert service._get_max_score(g) == 10

    def test_percentage_scale(self, service):
        g = _make_guideline("g1", "percentage")
        assert service._get_max_score(g) == 100

    def test_custom_category_scale(self, service):
        g = _make_guideline(
            "g1", "custom_category", {"categories": ["bad", "ok", "good", "great"]}
        )
        assert service._get_max_score(g) == 3

    def test_custom_category_empty(self, service):
        g = _make_guideline("g1", "custom_category", {"categories": []})
        assert service._get_max_score(g) == 1

    def test_custom_category_no_categories(self, service):
        g = _make_guideline("g1", "custom_category", {})
        assert service._get_max_score(g) == 1

    def test_unknown_scale_defaults_to_1(self, service):
        g = _make_guideline("g1", "unknown_type")
        assert service._get_max_score(g) == 1


class TestBuildEntry:
    def test_valid_numeric_trace(self, service):
        trace = _make_trace(
            1,
            ["quality"],
            {"scores": {"quality": {"type": "numeric", "mean": 4.0, "failed": 1}}},
        )
        guidelines = {"quality": _make_guideline("quality", "numeric", {"max_value": 5})}

        entry = service._build_entry(trace, guidelines)

        assert entry is not None
        assert entry.trace_id == 1
        assert len(entry.scores) == 1
        assert entry.scores[0].mean == 4.0
        assert entry.scores[0].max_score == 5
        assert entry.scores[0].normalized == round(4.0 / 5, 4)
        assert entry.total_failures == 1

    def test_categorical_trace(self, service):
        trace = _make_trace(
            2,
            ["sentiment"],
            {
                "scores": {
                    "sentiment": {
                        "type": "categorical",
                        "distribution": {"1": 3, "2": 7},
                        "failed": 0,
                    }
                }
            },
        )
        guidelines = {
            "sentiment": _make_guideline(
                "sentiment", "custom_category", {"categories": ["bad", "ok", "good"]}
            )
        }

        entry = service._build_entry(trace, guidelines)

        assert entry is not None
        expected_mean = (1 * 3 + 2 * 7) / 10
        assert entry.scores[0].mean == expected_mean

    def test_categorical_empty_distribution(self, service):
        trace = _make_trace(
            3,
            ["rating"],
            {"scores": {"rating": {"type": "categorical", "distribution": {}, "failed": 0}}},
        )
        guidelines = {
            "rating": _make_guideline("rating", "custom_category", {"categories": ["a", "b"]})
        }

        entry = service._build_entry(trace, guidelines)
        assert entry is not None
        assert entry.scores[0].mean == 0.0

    def test_no_summary_returns_none(self, service):
        trace = _make_trace(4, ["g1"], None)
        entry = service._build_entry(trace, {})
        assert entry is None

    def test_no_scores_in_summary_returns_none(self, service):
        trace = _make_trace(5, ["g1"], {"other": "data"})
        entry = service._build_entry(trace, {})
        assert entry is None

    def test_missing_guideline_in_db_skips(self, service):
        trace = _make_trace(
            6,
            ["g1"],
            {"scores": {"g1": {"type": "numeric", "mean": 3.0, "failed": 0}}},
        )
        entry = service._build_entry(trace, {})
        assert entry is None

    def test_missing_score_for_guideline_skips(self, service):
        trace = _make_trace(
            7,
            ["g1", "g2"],
            {"scores": {"g1": {"type": "numeric", "mean": 5.0, "failed": 0}}},
        )
        guidelines = {
            "g1": _make_guideline("g1", "numeric", {"max_value": 10}),
            "g2": _make_guideline("g2", "numeric", {"max_value": 10}),
        }

        entry = service._build_entry(trace, guidelines)
        assert entry is not None
        assert len(entry.scores) == 1

    def test_multiple_guidelines_averaged(self, service):
        trace = _make_trace(
            8,
            ["g1", "g2"],
            {
                "scores": {
                    "g1": {"type": "numeric", "mean": 5.0, "failed": 0},
                    "g2": {"type": "numeric", "mean": 10.0, "failed": 2},
                }
            },
        )
        guidelines = {
            "g1": _make_guideline("g1", "numeric", {"max_value": 10}),
            "g2": _make_guideline("g2", "numeric", {"max_value": 10}),
        }

        entry = service._build_entry(trace, guidelines)
        assert entry is not None
        assert entry.normalized_avg_score == round((0.5 + 1.0) / 2, 4)
        assert entry.total_failures == 2


class TestGetLeaderboard:
    async def test_dataset_not_found(self, service):
        service.repository.get_dataset_by_name.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_leaderboard("missing")

    async def test_no_traces_returns_empty(self, service):
        dataset = MagicMock()
        dataset.sample_count = 100
        service.repository.get_dataset_by_name.return_value = dataset
        service.repository.get_completed_traces_by_dataset.return_value = []

        result = await service.get_leaderboard("test_ds")
        assert result.entries == []
        assert result.dataset_name == "test_ds"

    async def test_leaderboard_sorted_descending(self, service):
        dataset = MagicMock()
        dataset.sample_count = 50
        service.repository.get_dataset_by_name.return_value = dataset

        trace_low = _make_trace(
            1, ["g1"],
            {"scores": {"g1": {"type": "numeric", "mean": 2.0, "failed": 0}}},
        )
        trace_high = _make_trace(
            2, ["g1"],
            {"scores": {"g1": {"type": "numeric", "mean": 8.0, "failed": 0}}},
        )
        service.repository.get_completed_traces_by_dataset.return_value = [
            trace_low,
            trace_high,
        ]
        service.repository.get_guidelines_by_names.return_value = {
            "g1": _make_guideline("g1", "numeric", {"max_value": 10})
        }

        result = await service.get_leaderboard("test_ds")
        assert len(result.entries) == 2
        assert result.entries[0].trace_id == 2
        assert result.entries[1].trace_id == 1
