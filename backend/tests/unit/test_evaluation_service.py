"""Unit tests for EvaluationService helper and async methods."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from api.core.exceptions import NotFoundException
from api.evaluations.schemas import (
    EvaluationRequest,
    FlexibleEvaluationRequest,
    JudgeType,
    ModelConfig,
    OutputType,
    TaskEvaluationRequest,
    DatasetConfig,
    TextOutputConfig,
    TraceSamplesRequest,
)
from api.evaluations.service import (
    EvaluationService,
    get_process_pool,
    shutdown_process_pool,
    _recreate_process_pool,
    _process_pool,
)
from api.guidelines.schemas import GuidelineScoringScale


def _model_config(**overrides):
    defaults = dict(
        api_source="standard",
        model_name="gpt-4o-mini",
        model_id=1,
        api_name="gpt-4o-mini",
        model_provider="openai",
        model_provider_slug="openai",
        model_provider_id=1,
    )
    defaults.update(overrides)
    return ModelConfig(**defaults)


def _mock_guideline(name="quality", scoring_scale="numeric", config=None):
    g = MagicMock()
    g.name = name
    g.prompt = "Rate the quality"
    g.scoring_scale = scoring_scale
    g.scoring_scale_config = config or {"min_value": 1, "max_value": 5}
    return g


@pytest.fixture
def service():
    mock_session = AsyncMock()
    with patch("api.evaluations.service.S3Storage") as MockS3, \
         patch("api.evaluations.service.EvaluationRepository") as MockRepo, \
         patch("api.evaluations.service.GuidelineService") as MockGuideline, \
         patch("api.evaluations.service.ModelsAndProvidersService") as MockModels:
        svc = EvaluationService(mock_session, "user-uuid-123")
        svc.repository = AsyncMock()
        svc.guideline_service = AsyncMock()
        svc.s3 = MagicMock()
        svc.model_providers_service = AsyncMock()
        yield svc


# ==================== Process Pool Functions ====================


class TestProcessPool:
    def test_get_process_pool_creates_pool(self):
        import api.evaluations.service as svc_mod
        original = svc_mod._process_pool
        svc_mod._process_pool = None
        try:
            pool = get_process_pool()
            assert pool is not None
        finally:
            if svc_mod._process_pool is not None:
                svc_mod._process_pool.shutdown(wait=False)
            svc_mod._process_pool = original

    def test_shutdown_process_pool(self):
        import api.evaluations.service as svc_mod
        original = svc_mod._process_pool
        svc_mod._process_pool = None
        get_process_pool()
        shutdown_process_pool()
        assert svc_mod._process_pool is None
        svc_mod._process_pool = original

    def test_recreate_process_pool(self):
        import api.evaluations.service as svc_mod
        original = svc_mod._process_pool
        svc_mod._process_pool = None
        pool = _recreate_process_pool()
        assert pool is not None
        pool.shutdown(wait=False)
        svc_mod._process_pool = original


# ==================== Pure Helper Methods ====================


class TestToStoredConfig:
    def test_standard_config(self, service):
        config = _model_config()
        result = service._to_stored_config(config)
        assert result == {
            "api_source": "standard",
            "api_name": "gpt-4o-mini",
            "provider_slug": "openai",
        }

    def test_openrouter_config(self, service):
        config = _model_config(api_source="openrouter", model_provider_slug="anthropic")
        result = service._to_stored_config(config)
        assert result["api_source"] == "openrouter"
        assert result["provider_slug"] == "anthropic"


class TestBuildTaskName:
    def test_simple_task_name(self, service):
        request = MagicMock()
        request.task_name = "gsm8k"
        request.dataset_config.n_fewshots = 5
        result = service._build_task_name(request)
        assert result == "gsm8k|5"

    def test_task_name_with_pipe(self, service):
        request = MagicMock()
        request.task_name = "gsm8k|0"
        result = service._build_task_name(request)
        assert result == "gsm8k|0"

    def test_task_name_none_fewshots(self, service):
        request = MagicMock()
        request.task_name = "mmlu"
        request.dataset_config.n_fewshots = None
        result = service._build_task_name(request)
        assert result == "mmlu|None"


class TestConvertGuidelineToDict:
    def test_numeric_guideline(self, service):
        g = _mock_guideline("quality", GuidelineScoringScale.NUMERIC, {"min_value": 1, "max_value": 5})
        result = service._convert_guideline_to_dict(g)
        assert result["name"] == "quality"
        assert result["scoring_scale_config"]["min_value"] == 1
        assert result["scoring_scale_config"]["max_value"] == 5

    def test_custom_category_guideline(self, service):
        g = _mock_guideline("sentiment", GuidelineScoringScale.CUSTOM_CATEGORY,
                            {"categories": ["good", "bad"]})
        result = service._convert_guideline_to_dict(g)
        assert result["scoring_scale_config"]["categories"] == ["good", "bad"]

    def test_boolean_guideline(self, service):
        g = _mock_guideline("helpful", GuidelineScoringScale.BOOLEAN, {})
        result = service._convert_guideline_to_dict(g)
        assert result["scoring_scale_config"] == {}

    def test_percentage_guideline(self, service):
        g = _mock_guideline("accuracy", GuidelineScoringScale.PERCENTAGE, {})
        result = service._convert_guideline_to_dict(g)
        assert result["scoring_scale_config"] == {}


class TestExtractSummary:
    def test_numeric_scores(self, service):
        pipeline_output = {
            "scores": {"quality": [3.0, 4.0, 5.0]},
            "sample_count": 3,
        }
        guidelines = [_mock_guideline("quality", GuidelineScoringScale.NUMERIC)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["quality"]["type"] == "numeric"
        assert result["quality"]["mean"] == 4.0
        assert result["quality"]["failed"] == 0

    def test_numeric_empty_scores(self, service):
        pipeline_output = {"scores": {"quality": []}, "sample_count": 5}
        guidelines = [_mock_guideline("quality", GuidelineScoringScale.NUMERIC)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["quality"]["mean"] == 0.0
        assert result["quality"]["failed"] == 5

    def test_boolean_scores(self, service):
        pipeline_output = {
            "scores": {"helpful": ["true", "false", "true"]},
            "sample_count": 3,
        }
        guidelines = [_mock_guideline("helpful", GuidelineScoringScale.BOOLEAN)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["helpful"]["type"] == "categorical"
        assert result["helpful"]["distribution"] == {"true": 2, "false": 1}
        assert result["helpful"]["mode"] == "true"

    def test_custom_category_scores(self, service):
        pipeline_output = {
            "scores": {"sentiment": ["good", "good", "bad"]},
            "sample_count": 4,
        }
        guidelines = [_mock_guideline("sentiment", GuidelineScoringScale.CUSTOM_CATEGORY)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["sentiment"]["type"] == "categorical"
        assert result["sentiment"]["failed"] == 1

    def test_percentage_scores(self, service):
        pipeline_output = {
            "scores": {"accuracy": [80, 90, 85]},
            "sample_count": 3,
        }
        guidelines = [_mock_guideline("accuracy", GuidelineScoringScale.PERCENTAGE)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["accuracy"]["type"] == "numeric"
        assert result["accuracy"]["mean"] == 85.0

    def test_missing_metric_key(self, service):
        pipeline_output = {"scores": {}, "sample_count": 3}
        guidelines = [_mock_guideline("missing_metric")]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["missing_metric"]["failed"] == 3

    def test_single_score_no_stdev(self, service):
        pipeline_output = {"scores": {"q": [5.0]}, "sample_count": 1}
        guidelines = [_mock_guideline("q", GuidelineScoringScale.NUMERIC)]
        result = service._extract_summary(pipeline_output, guidelines)
        assert result["q"]["std"] == 0.0


class TestExtractTaskSummary:
    def test_basic_extraction(self, service):
        pipeline_output = {
            "summary": {"exact_match": 0.85, "exact_match_stderr": 0.03, "f1": 0.92, "f1_stderr": 0.02}
        }
        result = service._extract_task_summary(pipeline_output)
        assert "exact_match" in result
        assert result["exact_match"]["mean"] == 0.85
        assert result["exact_match"]["std"] == 0.03
        assert "exact_match_stderr" not in result
        assert result["f1"]["mean"] == 0.92

    def test_no_stderr(self, service):
        pipeline_output = {"summary": {"accuracy": 0.75}}
        result = service._extract_task_summary(pipeline_output)
        assert result["accuracy"]["std"] == 0


class TestExtractFlexibleSummary:
    def test_llm_judge_delegates(self, service):
        request = MagicMock()
        request.judge_type = JudgeType.LLM_AS_JUDGE
        guidelines = [_mock_guideline("q", GuidelineScoringScale.NUMERIC)]
        pipeline_output = {"scores": {"q": [4.0, 5.0]}, "sample_count": 2}

        result = service._extract_flexible_summary(pipeline_output, request, guidelines)
        assert result["q"]["type"] == "numeric"

    def test_exact_match_scalar_score(self, service):
        request = MagicMock()
        request.judge_type = JudgeType.EXACT_MATCH
        pipeline_output = {"scores": {"exact_match": 0.9}, "sample_count": 10}

        result = service._extract_flexible_summary(pipeline_output, request, [])
        assert result["exact_match"]["mean"] == 0.9
        assert result["exact_match"]["type"] == "numeric"

    def test_f1_list_scores(self, service):
        request = MagicMock()
        request.judge_type = JudgeType.F1_SCORE
        pipeline_output = {"scores": {"f1": [0.8, 0.9, 1.0]}, "sample_count": 3}

        result = service._extract_flexible_summary(pipeline_output, request, [])
        assert result["f1"]["type"] == "numeric"
        assert 0.89 < result["f1"]["mean"] < 0.91

    def test_empty_list_scores(self, service):
        request = MagicMock()
        request.judge_type = JudgeType.EXACT_MATCH
        pipeline_output = {"scores": {"em": []}, "sample_count": 5}

        result = service._extract_flexible_summary(pipeline_output, request, [])
        assert result["em"]["mean"] == 0.0
        assert result["em"]["failed"] == 5


# ==================== Async Methods ====================


class TestCreateTrace:
    async def test_creates_trace(self, service):
        mock_trace = MagicMock(id=1, created_at=datetime.now())
        service.repository.create_trace.return_value = mock_trace

        request = EvaluationRequest(
            dataset_name="test_ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )
        result = await service._create_trace(request)
        assert result.id == 1
        service.repository.create_trace.assert_called_once()


class TestCreateTaskTrace:
    async def test_with_judge_config(self, service):
        mock_trace = MagicMock(id=2, created_at=datetime.now())
        service.repository.create_trace.return_value = mock_trace

        request = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k", n_samples=10),
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )
        result = await service._create_task_trace(request)
        assert result.id == 2

    async def test_without_judge_config(self, service):
        mock_trace = MagicMock(id=3, created_at=datetime.now())
        service.repository.create_trace.return_value = mock_trace

        request = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k"),
            model_completion_config=_model_config(),
        )
        result = await service._create_task_trace(request)
        call_kwargs = service.repository.create_trace.call_args.kwargs
        assert call_kwargs["judge_model_config"]["api_name"] == ""


class TestCreateFlexibleTrace:
    async def test_with_llm_judge(self, service):
        mock_trace = MagicMock(id=4, created_at=datetime.now())
        service.repository.create_trace.return_value = mock_trace

        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.LLM_AS_JUDGE,
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )
        result = await service._create_flexible_trace(request)
        call_kwargs = service.repository.create_trace.call_args.kwargs
        assert call_kwargs["guideline_names"] == ["g1"]

    async def test_with_exact_match(self, service):
        mock_trace = MagicMock(id=5, created_at=datetime.now())
        service.repository.create_trace.return_value = mock_trace

        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            model_completion_config=_model_config(),
        )
        await service._create_flexible_trace(request)
        call_kwargs = service.repository.create_trace.call_args.kwargs
        assert call_kwargs["guideline_names"] == ["exact_match"]


class TestLoadDatasetContent:
    def test_delegates_to_s3(self, service):
        service.s3.download_dataset.return_value = '{"input": "hello"}'
        result = service._load_dataset_content("my_ds")
        assert result == '{"input": "hello"}'


class TestLoadGuidelines:
    async def test_loads_guidelines(self, service):
        g1 = _mock_guideline("g1")
        g2 = _mock_guideline("g2")
        service.guideline_service.get_guideline_by_name.side_effect = [g1, g2]
        result = await service._load_guidelines(["g1", "g2"])
        assert len(result) == 2


class TestUpdateTraceGuidelines:
    async def test_updates_guidelines(self, service):
        trace = MagicMock()
        trace.guideline_names = []
        result = await service._update_trace_guidelines(trace, ["g1", "g2"])
        assert trace.guideline_names == ["g1", "g2"]

    async def test_empty_guidelines_noop(self, service):
        trace = MagicMock()
        result = await service._update_trace_guidelines(trace, [])
        service.session.commit.assert_not_called()


class TestGetModelApiNameAndBaseUrl:
    async def test_success(self, service):
        provider = MagicMock()
        provider.base_url = "https://api.openai.com/v1"
        model = MagicMock()
        model.api_name = "gpt-4o"
        service.model_providers_service.get_provider.return_value = provider
        service.model_providers_service.get_model.return_value = model

        name, url = await service._get_model_api_name_and_base_url(1, 1)
        assert name == "gpt-4o"
        assert url == "https://api.openai.com/v1"


class TestGetSerializableModelConfig:
    async def test_standard_source(self, service):
        service.s3.download_api_key.return_value = "sk-key"
        provider = MagicMock(base_url="https://api.openai.com/v1")
        model = MagicMock(api_name="gpt-4o")
        service.model_providers_service.get_provider.return_value = provider
        service.model_providers_service.get_model.return_value = model

        config = _model_config()
        result = await service._get_serializable_model_config(config)
        assert result["model_name"] == "gpt-4o"
        assert result["api_key"] == "sk-key"

    async def test_openrouter_source(self, service):
        service.s3.download_api_key.return_value = "or-key"

        config = _model_config(api_source="openrouter", api_name="anthropic/claude-3")
        result = await service._get_serializable_model_config(config)
        assert result["model_name"] == "anthropic/claude-3"
        assert result["base_url"] == "https://openrouter.ai/api/v1"
        assert "extra_body" in result


class TestCreateJudgeClientParameters:
    async def test_standard_source(self, service):
        service.s3.download_api_key.return_value = "sk-judge"
        provider = MagicMock(base_url="https://api.openai.com/v1")
        model = MagicMock(api_name="gpt-4o")
        service.model_providers_service.get_provider.return_value = provider
        service.model_providers_service.get_model.return_value = model

        config = _model_config()
        result = await service._create_judge_client_parameters(config)
        assert result["api_key"] == "sk-judge"

    async def test_openrouter_source(self, service):
        service.s3.download_api_key.return_value = "or-key"

        config = _model_config(api_source="openrouter", model_provider_slug="anthropic")
        result = await service._create_judge_client_parameters(config)
        assert result["base_url"] == "https://openrouter.ai/api/v1"
        assert result["extra_body"]["provider"]["order"] == ["anthropic"]


class TestWriteResults:
    async def test_writes_events(self, service):
        trace = MagicMock(id=1)
        request = EvaluationRequest(
            dataset_name="ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )
        pipeline_output = {
            "sample_count": 10,
            "temp_dir": "/tmp/results",
            "summary": {"g1": {"mean": 4.0}},
        }
        service.s3.upload_eval_results.return_value = "eval_results/1"

        await service._write_results(trace, request, pipeline_output)
        assert service.repository.create_event.call_count == 3

    async def test_writes_task_results(self, service):
        trace = MagicMock(id=1)
        request = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k", n_samples=10, n_fewshots=5),
            model_completion_config=_model_config(),
        )
        pipeline_output = {
            "sample_count": 10,
            "temp_dir": "/tmp/results",
            "summary": {"exact_match": 0.85},
        }
        service.s3.upload_eval_results.return_value = "eval_results/1"

        await service._write_task_results(trace, request, pipeline_output, ["exact_match"])
        assert service.repository.create_event.call_count == 3

    async def test_writes_flexible_results(self, service):
        trace = MagicMock(id=1)
        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            model_completion_config=_model_config(),
        )
        pipeline_output = {
            "sample_count": 5,
            "temp_dir": "/tmp/results",
            "summary": {"em": 0.8},
        }
        service.s3.upload_eval_results.return_value = "eval_results/1"

        await service._write_flexible_results(trace, request, pipeline_output, ["em"])
        assert service.repository.create_event.call_count == 3


class TestUploadTraceJsonlSimple:
    async def test_uploads_events(self, service):
        trace = MagicMock(id=1, completion_model="gpt-4o", dataset_name="ds")
        event = MagicMock(
            event_type="spec",
            trace_id=1,
            sample_id=None,
            guideline_name=None,
            data={"key": "value"},
            created_at=datetime(2025, 1, 1),
        )
        service.repository.get_events_by_trace.return_value = [event]

        await service._upload_trace_jsonl_simple(trace)
        service.s3.upload_trace.assert_called_once()
        call_args = service.s3.upload_trace.call_args
        assert "gpt-4o" in call_args[0][0]

    async def test_handles_slash_in_model_name(self, service):
        trace = MagicMock(id=1, completion_model="anthropic/claude-3", dataset_name="ds")
        service.repository.get_events_by_trace.return_value = []

        await service._upload_trace_jsonl_simple(trace)
        filename = service.s3.upload_trace.call_args[0][0]
        assert "/" not in filename.split("_", 1)[1].split("-", 1)[0]


class TestGetTrace:
    async def test_authorized_user(self, service):
        trace = MagicMock(user_id="user-uuid-123")
        service.repository.get_trace_by_id.return_value = trace

        result = await service.get_trace(1)
        assert result == trace

    async def test_unauthorized_user(self, service):
        trace = MagicMock(user_id="different-user")
        service.repository.get_trace_by_id.return_value = trace

        with pytest.raises(HTTPException) as exc_info:
            await service.get_trace(1)
        assert exc_info.value.status_code == 403


class TestGetTraces:
    async def test_returns_traces(self, service):
        traces = [MagicMock(), MagicMock()]
        service.repository.get_traces_by_user.return_value = traces

        result = await service.get_traces()
        assert len(result) == 2
        service.repository.get_traces_by_user.assert_called_once_with("user-uuid-123")


class TestGetTraceDetails:
    async def test_returns_details(self, service):
        trace = MagicMock(id=1, user_id="user-uuid-123", status="completed",
                          created_at=datetime.now(), judge_model_provider="openai")
        service.repository.get_trace_by_id.return_value = trace
        spec_event = MagicMock(data={"dataset_name": "ds"})
        service.repository.get_spec_event_by_trace_id.return_value = spec_event

        result = await service.get_trace_details(1)
        assert result.trace_id == 1
        assert result.spec == {"dataset_name": "ds"}

    async def test_no_spec_event_raises(self, service):
        trace = MagicMock(id=1, user_id="user-uuid-123")
        service.repository.get_trace_by_id.return_value = trace
        service.repository.get_spec_event_by_trace_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_trace_details(1)


# ==================== Background Methods ====================


class TestRunEvaluationBackground:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_trace = MagicMock(
            id=1, user_id="user-123", created_at=datetime.now(),
            completion_model="gpt-4o", dataset_name="ds"
        )
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace
        mock_repo.get_events_by_trace.return_value = []

        pipeline_output = {
            "success": True,
            "summary": {"g1": {"mean": 4.0}},
            "scores": {"g1": [4.0, 5.0]},
            "sample_count": 2,
            "temp_dir": "/tmp/test",
        }

        request = EvaluationRequest(
            dataset_name="ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None) as mock_init, \
             patch("api.evaluations.service.EvaluationService._load_dataset_content", return_value='{"input":"hi"}'), \
             patch("api.evaluations.service.EvaluationService._load_guidelines", new_callable=AsyncMock, return_value=[_mock_guideline("g1", GuidelineScoringScale.NUMERIC)]), \
             patch("api.evaluations.service.EvaluationService._convert_guideline_to_dict", return_value={"name": "g1"}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={"model_name": "gpt-4o"}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_judge_config", new_callable=AsyncMock, return_value={"model_name": "gpt-4o"}), \
             patch("api.evaluations.service.get_process_pool") as mock_pool, \
             patch("asyncio.get_event_loop") as mock_loop, \
             patch("api.evaluations.service.EvaluationService._write_results", new_callable=AsyncMock), \
             patch("api.evaluations.service.EvaluationService._extract_summary", return_value={"g1": {"mean": 4.0}}), \
             patch("api.evaluations.service.EvaluationService._upload_trace_jsonl_simple", new_callable=AsyncMock):

            mock_loop.return_value.run_in_executor = AsyncMock(return_value=pipeline_output)

            await EvaluationService._run_evaluation_background(1, request)
            mock_repo.update_trace_status.assert_called()

    @pytest.mark.asyncio
    async def test_failure_updates_status(self):
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.side_effect = Exception("DB error")

        request = EvaluationRequest(
            dataset_name="ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo):
            await EvaluationService._run_evaluation_background(1, request)
            mock_repo.update_trace_status.assert_called_once()
            args = mock_repo.update_trace_status.call_args
            assert args[0][1] == "failed"

    @pytest.mark.asyncio
    async def test_broken_process_pool(self):
        from concurrent.futures.process import BrokenProcessPool

        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_trace = MagicMock(id=1, user_id="user-123")
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace

        request = EvaluationRequest(
            dataset_name="ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None), \
             patch("api.evaluations.service.EvaluationService._load_dataset_content", return_value="{}"), \
             patch("api.evaluations.service.EvaluationService._load_guidelines", new_callable=AsyncMock, return_value=[]), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_judge_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.get_process_pool"), \
             patch("asyncio.get_event_loop") as mock_loop, \
             patch("api.evaluations.service._recreate_process_pool"):

            mock_loop.return_value.run_in_executor = AsyncMock(side_effect=BrokenProcessPool())

            await EvaluationService._run_evaluation_background(1, request)
            mock_repo.update_trace_status.assert_called()
            assert mock_repo.update_trace_status.call_args[0][1] == "failed"

    @pytest.mark.asyncio
    async def test_worker_returns_failure(self):
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_trace = MagicMock(id=1, user_id="user-123")
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace

        request = EvaluationRequest(
            dataset_name="ds",
            guideline_names=["g1"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None), \
             patch("api.evaluations.service.EvaluationService._load_dataset_content", return_value="{}"), \
             patch("api.evaluations.service.EvaluationService._load_guidelines", new_callable=AsyncMock, return_value=[]), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_judge_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.get_process_pool"), \
             patch("asyncio.get_event_loop") as mock_loop:

            mock_loop.return_value.run_in_executor = AsyncMock(return_value={"success": False, "error": "OOM"})

            await EvaluationService._run_evaluation_background(1, request)
            mock_repo.update_trace_status.assert_called()
            assert mock_repo.update_trace_status.call_args[0][1] == "failed"


class TestRunTaskEvaluationBackground:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_session = AsyncMock()

        call_count = [0]
        async def fake_get_session():
            call_count[0] += 1
            yield mock_session

        mock_trace = MagicMock(
            id=1, user_id="user-123", created_at=datetime.now(),
            completion_model="gpt-4o", dataset_name="gsm8k",
            guideline_names=[]
        )
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace
        mock_repo.get_events_by_trace.return_value = []

        pipeline_output = {
            "success": True,
            "summary": {"exact_match": 0.85, "exact_match_stderr": 0.02},
            "scores": {"exact_match": 0.85},
            "sample_count": 10,
            "temp_dir": "/tmp/test",
            "metric_docs": {},
        }

        request = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k", n_samples=10, n_fewshots=0),
            model_completion_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={"model_name": "gpt-4o"}), \
             patch("api.evaluations.service.EvaluationService._build_task_name", return_value="gsm8k|0"), \
             patch("api.evaluations.service.get_process_pool"), \
             patch("asyncio.get_event_loop") as mock_loop, \
             patch("api.evaluations.service.EvaluationService._update_trace_guidelines", new_callable=AsyncMock, return_value=mock_trace), \
             patch("api.evaluations.service.EvaluationService._write_task_results", new_callable=AsyncMock), \
             patch("api.evaluations.service.EvaluationService._extract_task_summary", return_value={"exact_match": {"mean": 0.85}}), \
             patch("api.evaluations.service.EvaluationService._upload_trace_jsonl_simple", new_callable=AsyncMock):

            mock_loop.return_value.run_in_executor = AsyncMock(return_value=pipeline_output)

            await EvaluationService._run_task_evaluation_background(1, request)

    @pytest.mark.asyncio
    async def test_failure_updates_status(self):
        mock_session = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.side_effect = Exception("DB error")

        request = TaskEvaluationRequest(
            task_name="gsm8k",
            dataset_config=DatasetConfig(dataset_name="gsm8k", n_samples=10),
            model_completion_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo):
            await EvaluationService._run_task_evaluation_background(1, request)


class TestRunFlexibleEvaluationBackground:
    @pytest.mark.asyncio
    async def test_success_exact_match(self):
        mock_session = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_trace = MagicMock(
            id=1, user_id="user-123", created_at=datetime.now(),
            completion_model="gpt-4o", dataset_name="ds",
            guideline_names=[]
        )
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace
        mock_repo.get_events_by_trace.return_value = []

        pipeline_output = {
            "success": True,
            "summary": {"exact_match": 0.9},
            "scores": {"exact_match": [1, 1, 0]},
            "sample_count": 3,
            "temp_dir": "/tmp/test",
        }

        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            model_completion_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None), \
             patch("api.evaluations.service.EvaluationService._load_dataset_content", return_value="{}"), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.get_process_pool"), \
             patch("asyncio.get_event_loop") as mock_loop, \
             patch("api.evaluations.service.EvaluationService._write_flexible_results", new_callable=AsyncMock), \
             patch("api.evaluations.service.EvaluationService._extract_flexible_summary", return_value={"exact_match": 0.9}), \
             patch("api.evaluations.service.EvaluationService._upload_trace_jsonl_simple", new_callable=AsyncMock):

            mock_loop.return_value.run_in_executor = AsyncMock(return_value=pipeline_output)

            await EvaluationService._run_flexible_evaluation_background(1, request)

    @pytest.mark.asyncio
    async def test_success_llm_judge(self):
        mock_session = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_trace = MagicMock(
            id=1, user_id="user-123", created_at=datetime.now(),
            completion_model="gpt-4o", dataset_name="ds",
            guideline_names=[]
        )
        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.return_value = mock_trace
        mock_repo.get_events_by_trace.return_value = []

        pipeline_output = {
            "success": True,
            "summary": {"quality": {"mean": 4.5}},
            "scores": {"quality": [4.0, 5.0]},
            "sample_count": 2,
            "temp_dir": "/tmp/test",
        }

        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.LLM_AS_JUDGE,
            guideline_names=["quality"],
            model_completion_config=_model_config(),
            judge_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo), \
             patch("api.evaluations.service.EvaluationService.__init__", return_value=None), \
             patch("api.evaluations.service.EvaluationService._load_dataset_content", return_value="{}"), \
             patch("api.evaluations.service.EvaluationService._load_guidelines", new_callable=AsyncMock, return_value=[_mock_guideline("quality")]), \
             patch("api.evaluations.service.EvaluationService._convert_guideline_to_dict", return_value={"name": "quality"}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_model_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.EvaluationService._get_serializable_judge_config", new_callable=AsyncMock, return_value={}), \
             patch("api.evaluations.service.get_process_pool"), \
             patch("asyncio.get_event_loop") as mock_loop, \
             patch("api.evaluations.service.EvaluationService._write_flexible_results", new_callable=AsyncMock), \
             patch("api.evaluations.service.EvaluationService._extract_flexible_summary", return_value={"quality": {"mean": 4.5}}), \
             patch("api.evaluations.service.EvaluationService._upload_trace_jsonl_simple", new_callable=AsyncMock):

            mock_loop.return_value.run_in_executor = AsyncMock(return_value=pipeline_output)

            await EvaluationService._run_flexible_evaluation_background(1, request)

    @pytest.mark.asyncio
    async def test_failure_updates_status(self):
        mock_session = AsyncMock()

        async def fake_get_session():
            yield mock_session

        mock_repo = AsyncMock()
        mock_repo.get_trace_by_id.side_effect = Exception("DB error")

        request = FlexibleEvaluationRequest(
            dataset_name="ds",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            model_completion_config=_model_config(),
        )

        with patch("api.evaluations.service.get_session", fake_get_session), \
             patch("api.evaluations.service.EvaluationRepository", return_value=mock_repo):
            await EvaluationService._run_flexible_evaluation_background(1, request)


# ==================== get_trace_samples ====================


class TestGetTraceSamples:
    async def test_no_s3_files(self, service):
        trace = MagicMock(id=1, user_id="user-uuid-123")
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = []

        request = TraceSamplesRequest(trace_id=1, n_samples=3)
        result = await service.get_trace_samples(request)
        assert result.samples == []

    async def test_no_parquet_files(self, service):
        trace = MagicMock(id=1, user_id="user-uuid-123")
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value=["eval_results/1/details/log.json"]

        request = TraceSamplesRequest(trace_id=1, n_samples=3)
        result = await service.get_trace_samples(request)
        assert result.samples == []

    async def test_parquet_read_success(self, service):
        import io
        import os
        import tempfile

        import pandas as pd

        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=["accuracy"])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/test.parquet"]

        df = pd.DataFrame([
            {
                "doc": {"query": "What is 2+2?", "gold_index": 0, "choices": ["4", "5"]},
                "model_response": {"input": [{"content": "What is 2+2?"}], "text": ["4"]},
                "metric": {"accuracy": 1.0},
            },
            {
                "doc": {"query": "What is 3+3?", "gold_index": 1, "choices": ["5", "6"]},
                "model_response": {"input": [{"content": "What is 3+3?"}], "text": ["6"]},
                "metric": {"accuracy": 1.0},
            },
        ])

        with tempfile.TemporaryDirectory() as td:
            pq_path = os.path.join(td, "test.parquet")
            df.to_parquet(pq_path)
            pq_bytes = open(pq_path, "rb").read()

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(pq_bytes)

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=2)
        result = await service.get_trace_samples(request)
        assert len(result.samples) == 2
        assert result.samples[0].input == "What is 2+2?"
        assert result.samples[0].prediction == "4"
        assert result.samples[0].gold == "4"

    async def test_parquet_read_exception(self, service):
        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=[])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/bad.parquet"]

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(b"not a parquet file")

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=3)
        result = await service.get_trace_samples(request)
        assert result.samples == []

    async def test_parquet_with_string_text(self, service):
        import os
        import tempfile

        import pandas as pd

        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=["em"])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/test.parquet"]

        df = pd.DataFrame([
            {
                "doc": {"query": "Hi", "gold_index": None, "choices": ["hello"]},
                "model_response": {"input": [{"content": "Hi"}], "text": "hello"},
                "metric": {"em": True},
            },
        ])

        with tempfile.TemporaryDirectory() as td:
            pq_path = os.path.join(td, "test.parquet")
            df.to_parquet(pq_path)
            pq_bytes = open(pq_path, "rb").read()

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(pq_bytes)

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=1)
        result = await service.get_trace_samples(request)
        assert len(result.samples) == 1
        assert result.samples[0].prediction == "hello"

    async def test_parquet_gold_from_gold_idx_list(self, service):
        import os
        import tempfile

        import pandas as pd

        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=[])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/test.parquet"]

        df = pd.DataFrame([
            {
                "doc": {"query": "Q", "gold_index": [0, 2], "choices": ["A", "B", "C"]},
                "model_response": {"input": [{"content": "Q"}], "text": ["A"]},
                "metric": {"_dummy": 0},
            },
        ])

        with tempfile.TemporaryDirectory() as td:
            pq_path = os.path.join(td, "test.parquet")
            df.to_parquet(pq_path)
            pq_bytes = open(pq_path, "rb").read()

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(pq_bytes)

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=1)
        result = await service.get_trace_samples(request)
        assert result.samples[0].gold == ["A", "C"]

    async def test_parquet_fallback_input_from_doc(self, service):
        import os
        import tempfile

        import pandas as pd

        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=[])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/test.parquet"]

        df = pd.DataFrame([
            {
                "doc": {"query": "Fallback Q", "gold_index": None, "choices": []},
                "model_response": {"input": [], "text": ["ans"]},
                "metric": {"_dummy": 0},
            },
        ])

        with tempfile.TemporaryDirectory() as td:
            pq_path = os.path.join(td, "test.parquet")
            df.to_parquet(pq_path)
            pq_bytes = open(pq_path, "rb").read()

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(pq_bytes)

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=1)
        result = await service.get_trace_samples(request)
        assert result.samples[0].input == "Fallback Q"

    async def test_parquet_gold_index_no_choices(self, service):
        import os
        import tempfile

        import pandas as pd

        trace = MagicMock(id=1, user_id="user-uuid-123", guideline_names=[])
        service.repository.get_trace_by_id.return_value = trace
        service.s3.list_files.return_value = ["eval_results/1/details/test.parquet"]

        df = pd.DataFrame([
            {
                "doc": {"query": "Q", "gold_index": 42, "choices": []},
                "model_response": {"input": [{"content": "Q"}], "text": ["ans"]},
                "metric": {"_dummy": 0},
            },
        ])

        with tempfile.TemporaryDirectory() as td:
            pq_path = os.path.join(td, "test.parquet")
            df.to_parquet(pq_path)
            pq_bytes = open(pq_path, "rb").read()

        def fake_download(s3_key, local_path):
            with open(local_path, "wb") as f:
                f.write(pq_bytes)

        service.s3.download_file = MagicMock(side_effect=fake_download)

        request = TraceSamplesRequest(trace_id=1, n_samples=1)
        result = await service.get_trace_samples(request)
        assert result.samples[0].gold == "42"
