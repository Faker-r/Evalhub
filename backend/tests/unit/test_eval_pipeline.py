"""Unit tests for CustomTaskEvaluationPipeline."""

from unittest.mock import MagicMock, patch

import pytest

from api.evaluations.eval_pipeline.eval_pipeline import (
    CustomTaskEvaluationPipeline,
    CustomTaskEvaluationPipelineParameters,
)


@pytest.fixture
def mock_task():
    task = MagicMock()
    task.full_name = "test_task"
    task.get_docs.return_value = []
    task.metrics = []
    task.aggregation.return_value = {}
    return task


@pytest.fixture
def mock_tracker():
    tracker = MagicMock()
    return tracker


@pytest.fixture
def mock_model():
    model = MagicMock()
    model.greedy_until.return_value = []
    model.config = MagicMock()
    return model


class TestCustomTaskEvaluationPipelineParameters:
    def test_defaults(self):
        params = CustomTaskEvaluationPipelineParameters()
        assert params.max_samples is None
        assert params.save_details is True
        assert params.use_cache is True

    def test_custom(self):
        params = CustomTaskEvaluationPipelineParameters(
            max_samples=10, save_details=False, use_cache=False
        )
        assert params.max_samples == 10
        assert params.save_details is False


class TestInit:
    def test_default_params(self, mock_task, mock_tracker, mock_model):
        pipeline = CustomTaskEvaluationPipeline(
            task=mock_task,
            evaluation_tracker=mock_tracker,
            model=mock_model,
        )
        assert pipeline.params.max_samples is None
        assert pipeline.task == mock_task

    def test_custom_params(self, mock_task, mock_tracker, mock_model):
        params = CustomTaskEvaluationPipelineParameters(max_samples=5)
        pipeline = CustomTaskEvaluationPipeline(
            task=mock_task,
            evaluation_tracker=mock_tracker,
            model=mock_model,
            params=params,
        )
        assert pipeline.params.max_samples == 5

    def test_disable_cache(self, mock_task, mock_tracker, mock_model):
        mock_model._cache = MagicMock()
        params = CustomTaskEvaluationPipelineParameters(use_cache=False)
        pipeline = CustomTaskEvaluationPipeline(
            task=mock_task,
            evaluation_tracker=mock_tracker,
            model=mock_model,
            params=params,
        )
        assert pipeline.model._cache is None


class TestRunModel:
    def test_calls_greedy_until(self, mock_task, mock_tracker, mock_model):
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)
        docs = [MagicMock(), MagicMock()]
        mock_model.greedy_until.return_value = [MagicMock(), MagicMock()]

        result = pipeline._run_model(docs)
        mock_model.greedy_until.assert_called_once_with(docs)
        assert len(result) == 2


class TestComputeMetrics:
    def test_no_metrics(self, mock_task, mock_tracker, mock_model):
        mock_task.metrics = []
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)
        docs = [MagicMock(), MagicMock()]
        responses = [MagicMock(), MagicMock()]

        result = pipeline._compute_metrics(responses, docs)
        assert result == [{}, {}]

    def test_with_compute_metric(self, mock_task, mock_tracker, mock_model):
        metric_with_compute = MagicMock()
        metric_with_compute.compute.return_value = [
            {"custom_score": 0.9},
            {"custom_score": 0.8},
        ]
        mock_task.metrics = [metric_with_compute]
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)

        docs = [MagicMock(), MagicMock()]
        responses = [MagicMock(), MagicMock()]

        result = pipeline._compute_metrics(responses, docs)
        assert result[0]["custom_score"] == 0.9
        assert result[1]["custom_score"] == 0.8

    @patch("api.evaluations.eval_pipeline.eval_pipeline.apply_metric")
    def test_with_standard_metric(
        self, mock_apply, mock_task, mock_tracker, mock_model
    ):
        metric = MagicMock(spec=["category", "metric_name"])
        del metric.compute
        mock_task.metrics = [metric]
        mock_apply.return_value = [{"acc": 1.0}, {"acc": 0.0}]
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)

        docs = [MagicMock(), MagicMock()]
        responses = [MagicMock(), MagicMock()]

        result = pipeline._compute_metrics(responses, docs)
        assert result[0]["acc"] == 1.0


class TestAggregateMetrics:
    def test_aggregation(self, mock_task, mock_tracker, mock_model):
        mock_task.aggregation.return_value = {"acc": lambda v: sum(v) / len(v)}
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)

        samples = [{"acc": 1.0}, {"acc": 0.5}, {"acc": 0.75}]
        result = pipeline._aggregate_metrics(samples)
        assert abs(result["acc"] - 0.75) < 1e-6

    def test_empty_aggregation(self, mock_task, mock_tracker, mock_model):
        mock_task.aggregation.return_value = {}
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)

        result = pipeline._aggregate_metrics([{"acc": 1.0}])
        assert result == {}


class TestEvaluate:
    def test_full_pipeline(self, mock_task, mock_tracker, mock_model):
        doc = MagicMock()
        response = MagicMock()
        mock_task.get_docs.return_value = [doc]
        mock_model.greedy_until.return_value = [response]
        mock_task.metrics = []
        mock_task.aggregation.return_value = {"acc": lambda v: sum(v) / max(len(v), 1)}

        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)
        result = pipeline.evaluate()

        assert "summary" in result
        assert "scores" in result
        assert result["sample_count"] == 1
        mock_tracker.general_config_logger.log_model_info.assert_called_once()


class TestSaveAndPush:
    def test_calls_save(self, mock_task, mock_tracker, mock_model):
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)
        pipeline.save_and_push_results()
        mock_tracker.save.assert_called_once()


class TestShowResults:
    def test_calls_generate(self, mock_task, mock_tracker, mock_model):
        mock_tracker.generate_final_dict.return_value = {"key": "value"}
        pipeline = CustomTaskEvaluationPipeline(mock_task, mock_tracker, mock_model)
        result = pipeline.show_results()
        assert result == {"key": "value"}
