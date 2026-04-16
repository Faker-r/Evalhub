"""Unit tests for eval_worker pipeline functions (full coverage)."""

from unittest.mock import MagicMock, patch

import pytest


class TestRunLightevalPipelineWorker:
    @patch("api.evaluations.eval_worker.DatasetTask")
    @patch("api.evaluations.eval_worker.OpenAICompatibleClient")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.CustomTaskEvaluationPipeline")
    @patch("api.evaluations.eval_worker.GuidelineJudgeMetric")
    @patch("api.evaluations.eval_worker.Registry")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_success(self, mock_mkdtemp, MockRegistry, MockMetric, MockPipeline,
                     MockTracker, mock_create_cfg, MockClient, MockDatasetTask):
        from api.evaluations.eval_worker import run_lighteval_pipeline_worker

        mock_task = MagicMock()
        mock_task.config = MagicMock()
        MockDatasetTask.return_value.build_lighteval_task.return_value = mock_task

        mock_model = MagicMock()
        mock_model._cache = None
        MockClient.return_value = mock_model

        mock_pipeline_inst = MockPipeline.return_value
        mock_pipeline_inst.evaluate.return_value = {
            "summary": {"acc": 0.9},
            "scores": {"acc": [1, 0, 1]},
            "sample_count": 3,
        }

        result = run_lighteval_pipeline_worker(
            dataset_name="ds",
            dataset_content='{"input": "hello"}\n',
            guidelines_data=[{
                "name": "g1", "prompt": "rate", "scoring_scale": "boolean",
                "scoring_scale_config": {},
            }],
            model_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
            judge_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
        )
        assert result["success"] is True
        assert result["summary"] == {"acc": 0.9}
        assert result["temp_dir"] == "/tmp/test"

    def test_exception_returns_error(self):
        from api.evaluations.eval_worker import run_lighteval_pipeline_worker

        with patch("api.evaluations.eval_worker.GuidelineJudgeMetric", side_effect=Exception("boom")):
            result = run_lighteval_pipeline_worker(
                dataset_name="ds", dataset_content="", guidelines_data=[{"name": "g"}],
                model_config_data={}, judge_config_data={"model_name": "m", "base_url": "u", "api_key": "k"},
            )
        assert result["success"] is False
        assert "boom" in result["error"]


class TestRunLightevalTaskPipelineWorker:
    @patch("api.evaluations.eval_worker.MetricDocGenerator")
    @patch("api.evaluations.eval_worker.Registry")
    @patch("api.evaluations.eval_worker.Pipeline")
    @patch("api.evaluations.eval_worker.OpenAICompatibleClient")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_success(self, mock_mkdtemp, MockTracker, mock_create_cfg,
                     MockClient, MockPipeline, MockRegistry, MockDocGen):
        from api.evaluations.eval_worker import run_lighteval_task_pipeline_worker

        mock_pipeline = MockPipeline.return_value
        mock_pipeline.get_results.return_value = {
            "results": {"all": {"accuracy": 0.85, "accuracy_stderr": 0.02}},
            "config_general": {"max_samples": 10},
        }

        mock_config = MagicMock()
        mock_config.metrics = []
        mock_registry = MockRegistry.return_value
        mock_registry.task_to_configs = {"task|0": [mock_config]}

        MockDocGen.generate_metric_docs.return_value = {}

        result = run_lighteval_task_pipeline_worker(
            task_name="task",
            n_samples=10,
            n_fewshots=0,
            model_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
        )
        assert result["success"] is True
        assert result["scores"]["accuracy"] == 0.85

    @patch("api.evaluations.eval_worker.Pipeline")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_with_pipe_in_task_name(self, mock_mkdtemp, MockTracker, mock_create_cfg, MockPipeline):
        from api.evaluations.eval_worker import run_lighteval_task_pipeline_worker

        MockPipeline.side_effect = Exception("pipeline error")

        result = run_lighteval_task_pipeline_worker(
            task_name="custom|5",
            n_samples=None,
            n_fewshots=5,
            model_config_data={"model_name": "m", "base_url": "u", "api_key": "k"},
        )
        assert result["success"] is False

    def test_exception_returns_error(self):
        from api.evaluations.eval_worker import run_lighteval_task_pipeline_worker

        with patch("api.evaluations.eval_worker.EvaluationTracker", side_effect=Exception("fail")):
            with patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/x"):
                result = run_lighteval_task_pipeline_worker(
                    task_name="t", n_samples=5, n_fewshots=0,
                    model_config_data={"model_name": "m", "base_url": "u", "api_key": "k"},
                )
        assert result["success"] is False


class TestRunFlexibleLightevalPipelineWorker:
    @patch("api.evaluations.eval_worker.FlexibleDatasetTask")
    @patch("api.evaluations.eval_worker.OpenAICompatibleClient")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.CustomTaskEvaluationPipeline")
    @patch("api.evaluations.eval_worker.Registry")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_success_exact_match(self, mock_mkdtemp, MockRegistry, MockPipeline,
                                  MockTracker, mock_create_cfg, MockClient, MockFlexTask):
        from api.evaluations.eval_worker import run_flexible_lighteval_pipeline_worker

        mock_task = MagicMock()
        mock_task.config = MagicMock()
        MockFlexTask.return_value.build_lighteval_task.return_value = mock_task

        mock_model = MagicMock()
        mock_model._cache = None
        MockClient.return_value = mock_model

        mock_pipeline_inst = MockPipeline.return_value
        mock_pipeline_inst.evaluate.return_value = {
            "summary": {"exact_match": 0.9},
            "scores": {"exact_match": [1, 1, 0]},
            "sample_count": 3,
        }

        result = run_flexible_lighteval_pipeline_worker(
            dataset_name="ds",
            dataset_content='{"q": "hello"}\n',
            input_field="q",
            output_type="text",
            judge_type="exact_match",
            text_config={"gold_answer_field": "answer"},
            mc_config=None,
            guidelines_data=[],
            model_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
            judge_config_data=None,
        )
        assert result["success"] is True
        assert result["sample_count"] == 3

    @patch("api.evaluations.eval_worker.FlexibleDatasetTask")
    @patch("api.evaluations.eval_worker.OpenAICompatibleClient")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.CustomTaskEvaluationPipeline")
    @patch("api.evaluations.eval_worker.GuidelineJudgeMetric")
    @patch("api.evaluations.eval_worker.Registry")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_success_llm_judge(self, mock_mkdtemp, MockRegistry, MockMetric, MockPipeline,
                                MockTracker, mock_create_cfg, MockClient, MockFlexTask):
        from api.evaluations.eval_worker import run_flexible_lighteval_pipeline_worker

        mock_task = MagicMock()
        mock_task.config = MagicMock()
        MockFlexTask.return_value.build_lighteval_task.return_value = mock_task

        mock_model = MagicMock()
        mock_model._cache = None
        MockClient.return_value = mock_model

        mock_pipeline_inst = MockPipeline.return_value
        mock_pipeline_inst.evaluate.return_value = {
            "summary": {"quality": 4.5},
            "scores": {"quality": [4, 5]},
            "sample_count": 2,
        }

        result = run_flexible_lighteval_pipeline_worker(
            dataset_name="ds",
            dataset_content='{"q": "hello"}\n',
            input_field="q",
            output_type="text",
            judge_type="llm_as_judge",
            text_config=None,
            mc_config=None,
            guidelines_data=[{
                "name": "quality", "prompt": "rate", "scoring_scale": "numeric",
                "scoring_scale_config": {"min_value": 1, "max_value": 5},
            }],
            model_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
            judge_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
        )
        assert result["success"] is True

    @patch("api.evaluations.eval_worker.FlexibleDatasetTask")
    @patch("api.evaluations.eval_worker.OpenAICompatibleClient")
    @patch("api.evaluations.eval_worker._create_model_config")
    @patch("api.evaluations.eval_worker.EvaluationTracker")
    @patch("api.evaluations.eval_worker.CustomTaskEvaluationPipeline")
    @patch("api.evaluations.eval_worker.Registry")
    @patch("api.evaluations.eval_worker.tempfile.mkdtemp", return_value="/tmp/test")
    def test_success_mc_config(self, mock_mkdtemp, MockRegistry, MockPipeline,
                                MockTracker, mock_create_cfg, MockClient, MockFlexTask):
        from api.evaluations.eval_worker import run_flexible_lighteval_pipeline_worker

        mock_task = MagicMock()
        mock_task.config = MagicMock()
        MockFlexTask.return_value.build_lighteval_task.return_value = mock_task

        mock_model = MagicMock()
        mock_model._cache = None
        MockClient.return_value = mock_model

        mock_pipeline_inst = MockPipeline.return_value
        mock_pipeline_inst.evaluate.return_value = {
            "summary": {"mcq": 0.8},
            "scores": {"mcq": [1, 0, 1]},
            "sample_count": 3,
        }

        result = run_flexible_lighteval_pipeline_worker(
            dataset_name="ds",
            dataset_content='{"q": "hello"}\n',
            input_field="q",
            output_type="multiple_choice",
            judge_type="exact_match",
            text_config=None,
            mc_config={"choices_field": "choices", "gold_answer_field": "answer"},
            guidelines_data=[],
            model_config_data={"model_name": "gpt-4o", "base_url": "http://url", "api_key": "key"},
            judge_config_data=None,
        )
        assert result["success"] is True

    def test_exception_returns_error(self):
        from api.evaluations.eval_worker import run_flexible_lighteval_pipeline_worker

        result = run_flexible_lighteval_pipeline_worker(
            dataset_name="ds", dataset_content="", input_field="q",
            output_type="invalid_type", judge_type="exact_match",
            text_config=None, mc_config=None, guidelines_data=[],
            model_config_data={}, judge_config_data=None,
        )
        assert result["success"] is False
