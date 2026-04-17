"""Unit tests for EvaluationRepository."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.core.exceptions import NotFoundException
from api.evaluations.repository import EvaluationRepository


@pytest.fixture
def session():
    s = AsyncMock()
    return s


@pytest.fixture
def repo(session):
    return EvaluationRepository(session)


def _mock_execute_result(scalar_value=None, scalars_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    if scalars_value is not None:
        result.scalars.return_value.all.return_value = scalars_value
    return result


class TestCreateTrace:
    async def test_creates_trace(self, repo, session):
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 1

        session.refresh = fake_refresh

        trace = await repo.create_trace(
            user_id="user-123",
            dataset_name="ds",
            guideline_names=["g1"],
            completion_model_config={"api_source": "standard", "api_name": "gpt-4o", "provider_slug": "openai"},
            judge_model_config={"api_source": "standard", "api_name": "gpt-4o", "provider_slug": "openai"},
        )
        session.add.assert_called_once()
        session.commit.assert_called_once()
        assert trace.user_id == "user-123"
        assert trace.dataset_name == "ds"
        assert trace.status == "running"


class TestUpdateTraceStatus:
    async def test_updates_status(self, repo, session):
        trace = MagicMock(id=1, status="running", summary=None)
        session.execute.return_value = _mock_execute_result(scalar_value=trace)
        session.refresh = AsyncMock()

        result = await repo.update_trace_status(1, "completed", {"scores": {}})
        assert trace.status == "completed"
        assert trace.summary == {"scores": {}}
        session.commit.assert_called_once()

    async def test_updates_without_summary(self, repo, session):
        trace = MagicMock(id=1, status="running", summary=None)
        session.execute.return_value = _mock_execute_result(scalar_value=trace)
        session.refresh = AsyncMock()

        await repo.update_trace_status(1, "failed")
        assert trace.status == "failed"
        assert trace.summary is None


class TestGetTraceById:
    async def test_found(self, repo, session):
        trace = MagicMock(id=1)
        session.execute.return_value = _mock_execute_result(scalar_value=trace)

        result = await repo.get_trace_by_id(1)
        assert result.id == 1

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        with pytest.raises(NotFoundException):
            await repo.get_trace_by_id(999)


class TestGetTracesByUser:
    async def test_returns_list(self, repo, session):
        traces = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_execute_result(scalars_value=traces)

        result = await repo.get_traces_by_user("user-123")
        assert len(result) == 2


class TestCreateEvent:
    async def test_creates_event(self, repo, session):
        session.add = MagicMock()

        async def fake_refresh(obj, *_a, **_kw):
            obj.id = 10

        session.refresh = fake_refresh

        event = await repo.create_event(
            trace_id=1,
            event_type="spec",
            data={"key": "value"},
            sample_id="s1",
            guideline_name="g1",
        )
        session.add.assert_called_once()
        session.commit.assert_called_once()
        assert event.trace_id == 1
        assert event.event_type == "spec"
        assert event.sample_id == "s1"


class TestGetEventsByTrace:
    async def test_returns_events(self, repo, session):
        events = [MagicMock(id=1), MagicMock(id=2)]
        session.execute.return_value = _mock_execute_result(scalars_value=events)

        result = await repo.get_events_by_trace(1)
        assert len(result) == 2


class TestGetSpecEventByTraceId:
    async def test_found(self, repo, session):
        event = MagicMock(event_type="spec")
        session.execute.return_value = _mock_execute_result(scalar_value=event)

        result = await repo.get_spec_event_by_trace_id(1)
        assert result.event_type == "spec"

    async def test_not_found(self, repo, session):
        session.execute.return_value = _mock_execute_result(scalar_value=None)

        result = await repo.get_spec_event_by_trace_id(999)
        assert result is None
