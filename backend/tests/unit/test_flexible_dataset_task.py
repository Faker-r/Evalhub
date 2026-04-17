"""Unit tests for FlexibleDatasetTask."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.evaluations.eval_pipeline.flexible_dataset_task import FlexibleDatasetTask
from api.evaluations.schemas import (
    JudgeType,
    MultipleChoiceConfig,
    OutputType,
    TextOutputConfig,
)


@pytest.fixture
def text_task():
    return FlexibleDatasetTask(
        dataset_name="test_ds",
        dataset_content='{"question": "What is 1+1?", "answer": "2"}\n',
        input_field="question",
        output_type=OutputType.TEXT,
        judge_type=JudgeType.EXACT_MATCH,
        text_config=TextOutputConfig(gold_answer_field="answer"),
    )


@pytest.fixture
def mc_task():
    return FlexibleDatasetTask(
        dataset_name="mc_ds",
        dataset_content='{"q": "Capital of France?", "choices": ["Berlin", "Paris", "London"], "answer": 1}\n',
        input_field="q",
        output_type=OutputType.MULTIPLE_CHOICE,
        judge_type=JudgeType.EXACT_MATCH,
        mc_config=MultipleChoiceConfig(choices_field="choices", gold_answer_field="answer"),
    )


class TestGetMetrics:
    def test_llm_judge_returns_guideline_metrics(self):
        mock_metric = MagicMock()
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.LLM_AS_JUDGE,
            guideline_metrics=[mock_metric],
        )
        assert task._get_metrics() == [mock_metric]

    def test_f1_score(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.F1_SCORE,
        )
        metrics = task._get_metrics()
        assert len(metrics) == 1

    def test_exact_match_text(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
        )
        metrics = task._get_metrics()
        assert len(metrics) == 1

    def test_exact_match_mc(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.MULTIPLE_CHOICE,
            judge_type=JudgeType.EXACT_MATCH,
        )
        metrics = task._get_metrics()
        assert len(metrics) == 1


class TestCreatePromptFunction:
    def test_text_prompt_with_gold(self, text_task):
        fn = text_task._create_prompt_function()
        line = {"question": "What is 1+1?", "answer": "2"}
        doc = fn(line, None)
        assert doc.query == "What is 1+1?"
        assert doc.choices == ["2"]

    def test_text_prompt_without_gold(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="question",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.F1_SCORE,
        )
        fn = task._create_prompt_function()
        line = {"question": "What is AI?"}
        doc = fn(line, None)
        assert doc.query == "What is AI?"
        assert doc.choices == []

    def test_mc_prompt_with_integer_gold(self, mc_task):
        fn = mc_task._create_prompt_function()
        line = {"q": "Capital of France?", "choices": ["Berlin", "Paris", "London"], "answer": 1}
        doc = fn(line, None)
        assert "multiple choice" in doc.query.lower()
        assert doc.gold_index == 1
        assert doc.choices == ["0", "1", "2"]

    def test_mc_prompt_with_string_gold(self, mc_task):
        fn = mc_task._create_prompt_function()
        line = {"q": "Capital of France?", "choices": ["Berlin", "Paris", "London"], "answer": "Paris"}
        doc = fn(line, None)
        assert doc.gold_index == 1

    def test_text_prompt_with_list_gold(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            text_config=TextOutputConfig(gold_answer_field="answers"),
        )
        fn = task._create_prompt_function()
        line = {"q": "Name a color", "answers": ["red", "blue"]}
        doc = fn(line, None)
        assert doc.choices == ["red", "blue"]

    def test_text_prompt_with_no_gold_field(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
            text_config=TextOutputConfig(gold_answer_field=None),
        )
        fn = task._create_prompt_function()
        line = {"q": "Test"}
        doc = fn(line, None)
        assert doc.choices == []


class TestCreateGenerationGrammar:
    def test_mc_grammar(self, mc_task):
        grammar = mc_task._create_generation_grammar()
        assert grammar.type == "json"
        assert "choice_index" in str(grammar.value)


class TestBuildLightevalTask:
    @patch("api.evaluations.eval_pipeline.flexible_dataset_task.LightevalTask")
    def test_build_text_task(self, MockTask, text_task):
        MockTask.return_value = MagicMock()
        task = text_task.build_lighteval_task()
        MockTask.assert_called_once()
        assert text_task.temp_file is not None
        text_task.cleanup()

    @patch("api.evaluations.eval_pipeline.flexible_dataset_task.LightevalTask")
    def test_build_mc_task(self, MockTask, mc_task):
        MockTask.return_value = MagicMock()
        task = mc_task.build_lighteval_task()
        MockTask.assert_called_once()
        mc_task.cleanup()


class TestCleanup:
    def test_cleanup_removes_file(self, text_task):
        import tempfile
        text_task.temp_file = MagicMock()
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            f.write(b"test")
            temp_path = f.name
        text_task.temp_file.name = temp_path
        text_task.cleanup()
        assert not Path(temp_path).exists()

    def test_cleanup_no_file(self):
        task = FlexibleDatasetTask(
            dataset_name="ds",
            dataset_content="",
            input_field="q",
            output_type=OutputType.TEXT,
            judge_type=JudgeType.EXACT_MATCH,
        )
        task.cleanup()  # should not raise
