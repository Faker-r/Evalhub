"""Unit tests for EvaluationService (Celery-backed evaluations on main)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.evaluations.models import Trace
from api.evaluations.schemas import (
    DatasetConfig,
    FlexibleEvaluationRequest,
    JudgeType,
    OutputType,
    StandardEvaluationModelConfig,
    TaskEvaluationRequest,
    TextOutputConfig,
)
from api.evaluations.service import EvaluationService
from api.models_and_providers.schemas import ModelResponse, ProviderResponse


def _provider() -> ProviderResponse:
    return ProviderResponse(
        id="p-1",
        name="openai",
        slug="openai",
        base_url="https://api.openai.com/v1",
    )


def _model() -> ModelResponse:
    p = _provider()
    return ModelResponse(
        id="m-1",
        display_name="GPT-4o",
        developer="OpenAI",
        api_name="gpt-4o",
        providers=[p],
    )


def std_model_cfg() -> StandardEvaluationModelConfig:
    m = _model()
    p = m.providers[0]
    return StandardEvaluationModelConfig(api_source="standard", model=m, provider=p)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    return EvaluationService(mock_session, "user-uuid-123")


@pytest.mark.asyncio
class TestRunTaskEvaluation:
    async def test_dispatches_celery_task(self, service):
        trace = MagicMock(spec=Trace)
        trace.id = 42
        trace.created_at = datetime(2025, 1, 1)

        req = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k", n_samples=5),
            model_completion_config=std_model_cfg(),
        )

        with (
            patch.object(service, "_create_task_trace", AsyncMock(return_value=trace)),
            patch.object(
                service,
                "_get_serializable_model_config",
                AsyncMock(return_value={"model_name": "gpt-4o"}),
            ),
            patch.object(service, "_get_model_pricing", return_value=None),
            patch.object(service, "_build_task_name", return_value="gsm8k|0"),
            patch("api.evaluations.service.run_task_evaluation_task") as mock_task,
        ):
            mock_task.delay = MagicMock()
            resp = await service.run_task_evaluation(req)

            assert resp.trace_id == 42
            assert resp.status == "running"
            mock_task.delay.assert_called_once()


@pytest.mark.asyncio
class TestRunFlexibleEvaluation:
    async def test_dispatches_celery_task(self, service):
        trace = MagicMock(spec=Trace)
        trace.id = 99
        trace.created_at = datetime(2025, 1, 2)

        req = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            text_config=TextOutputConfig(gold_answer_field="answer"),
            model_completion_config=std_model_cfg(),
        )

        with (
            patch.object(
                service, "_create_flexible_trace", AsyncMock(return_value=trace)
            ),
            patch.object(
                service, "_load_dataset_content", return_value='{"question":"hi"}\n'
            ),
            patch.object(
                service,
                "_get_serializable_model_config",
                AsyncMock(return_value={"model_name": "gpt-4o"}),
            ),
            patch.object(service, "_get_model_pricing", return_value=None),
            patch("api.evaluations.service.run_flexible_evaluation_task") as mock_task,
        ):
            mock_task.delay = MagicMock()
            resp = await service.run_flexible_evaluation(req)

            assert resp.trace_id == 99
            mock_task.delay.assert_called_once()


class TestDisplayHelpers:
    def test_get_display_model_name_standard(self, service):
        assert service._get_display_model_name(std_model_cfg()) == "GPT-4o"

    def test_get_provider_slug_standard(self, service):
        assert service._get_provider_slug(std_model_cfg()) == "openai"
