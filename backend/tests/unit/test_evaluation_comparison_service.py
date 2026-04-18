"""Unit tests for EvaluationComparisonService."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.evaluation_comparison.schemas import (
    ModelProviderPair,
    OverlappingDatasetsResult,
    SideBySideReportResult,
)
from api.evaluation_comparison.service import EvaluationComparisonService


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return EvaluationComparisonService(session)


class TestGetOverlappingDatasets:
    async def test_empty_pairs(self, service):
        result = await service.get_overlapping_datasets([])
        assert result.count == 0
        assert result.dataset_names == []

    async def test_with_pairs_no_results(self, service, session):
        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result

        pairs = [ModelProviderPair(model="gpt-4o", provider="openai")]
        result = await service.get_overlapping_datasets(pairs)
        assert result.count == 0

    async def test_delegates_to_fetch(self, service):
        service._fetch_overlapping_data = AsyncMock(
            return_value=(["ds1", "ds2"], {}, {})
        )
        pairs = [ModelProviderPair(model="gpt-4o", provider="openai")]
        result = await service.get_overlapping_datasets(pairs)
        assert result.count == 2
        assert result.dataset_names == ["ds1", "ds2"]


class TestGenerateSideBySideReport:
    async def test_empty_pairs(self, service):
        service._fetch_overlapping_data = AsyncMock(return_value=([], {}, {}))
        pairs = []
        result = await service.generate_side_by_side_report(pairs)
        assert result.entries == []

    async def test_with_overlapping_data(self, service):
        trace = MagicMock()
        trace.id = 1
        trace.created_at = datetime(2025, 1, 1)
        trace.summary = {"scores": {"accuracy": {"mean": 0.85}}}

        by_dataset_pair = {"ds1": {("gpt-4o", "openai"): trace}}

        spec_event = MagicMock()
        spec_event.id = 10
        spec_event.trace_id = 1
        spec_event.event_type = "spec"
        spec_event.sample_id = None
        spec_event.guideline_name = None
        spec_event.data = {"key": "value"}
        spec_event.created_at = datetime(2025, 1, 1)

        service._fetch_overlapping_data = AsyncMock(
            return_value=(["ds1"], by_dataset_pair, {1: spec_event})
        )

        pairs = [ModelProviderPair(model="gpt-4o", provider="openai")]
        result = await service.generate_side_by_side_report(pairs)
        assert len(result.entries) == 1
        assert result.entries[0].model == "gpt-4o"
        assert result.entries[0].dataset_name == "ds1"
        assert result.entries[0].metric_name == "accuracy"

    async def test_no_scores_in_summary(self, service):
        trace = MagicMock()
        trace.id = 1
        trace.created_at = datetime(2025, 1, 1)
        trace.summary = {}

        by_dataset_pair = {"ds1": {("gpt-4o", "openai"): trace}}

        service._fetch_overlapping_data = AsyncMock(
            return_value=(["ds1"], by_dataset_pair, {1: None})
        )

        pairs = [ModelProviderPair(model="gpt-4o", provider="openai")]
        result = await service.generate_side_by_side_report(pairs)
        assert len(result.entries) == 0
        assert result.spec_by_trace[1] is None


class TestFetchOverlappingData:
    async def test_empty_pairs(self, service):
        overlapping, by_ds, specs = await service._fetch_overlapping_data([])
        assert overlapping == []

    async def test_no_traces_found(self, service, session):
        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result

        overlapping, by_ds, specs = await service._fetch_overlapping_data(
            [("gpt-4o", "openai")]
        )
        assert overlapping == []
