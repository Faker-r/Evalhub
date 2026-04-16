"""Extended tests for guideline_judge: WrappedJudgeLM and GuidelineJudgeMetric methods."""

import json
from collections import Counter
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from api.evaluations.eval_pipeline.guideline_judge import (
    GuidelineJudgeMetric,
    WrappedJudgeLM,
    generate_get_judge_prompt_function,
    process_judge_response,
    BooleanGuidelineScoringScale,
    PercentageGuidelineScoringScale,
    NumericGuidelineScoringScale,
    CustomCategoryGuidelineScoringScale,
    BooleanScoreResponse,
    PercentageScoreResponse,
)
from api.guidelines.schemas import GuidelineScoringScale


class TestProcessJudgeResponse:
    def test_basemodel_response(self):
        class Resp(BaseModel):
            score: int

        resp = Resp(score=5)
        assert process_judge_response(resp) == 5

    def test_string_response(self):
        resp = json.dumps({"score": "true"})
        assert process_judge_response(resp) == "true"

    def test_numeric_string_response(self):
        resp = json.dumps({"score": 85})
        assert process_judge_response(resp) == 85


class TestGenerateGetJudgePromptFunction:
    def test_with_gold(self):
        guideline = {
            "prompt": "Rate quality",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
        }
        scale = BooleanGuidelineScoringScale()
        fn = generate_get_judge_prompt_function(guideline, scale)

        result = fn(question="What is AI?", answer="It is artificial intelligence", gold="correct answer")
        assert len(result) == 1
        assert "gold answer" in result[0]["content"].lower()
        assert "Rate quality" in result[0]["content"]

    def test_without_gold(self):
        guideline = {
            "prompt": "Rate quality",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
        }
        scale = NumericGuidelineScoringScale()
        fn = generate_get_judge_prompt_function(guideline, scale)

        result = fn(question="Q?", answer="A")
        assert "gold answer" not in result[0]["content"].lower()
        assert "1 to 5" in result[0]["content"]


class TestWrappedJudgeLM:
    def test_lazy_load_creates_client(self):
        wrapped = WrappedJudgeLM(
            model="gpt-4",
            templates=MagicMock(),
            process_judge_response=MagicMock(),
            url="https://api.openai.com/v1",
            api_key="sk-key",
        )
        wrapped.client = None

        with patch("api.evaluations.eval_pipeline.guideline_judge.OpenAI") as MockOpenAI:
            result = wrapped._lazy_load_client()
            MockOpenAI.assert_called_once_with(api_key="sk-key", base_url="https://api.openai.com/v1")
            assert result == wrapped._call_api_parallel

    def test_evaluate_answer(self):
        wrapped = WrappedJudgeLM(
            model="gpt-4",
            templates=MagicMock(return_value=[{"role": "user", "content": "test"}]),
            process_judge_response=MagicMock(return_value=5),
            url="https://api.openai.com/v1",
            api_key="sk-key",
        )
        wrapped.client = MagicMock()

        with patch.object(wrapped, "_lazy_load_client") as mock_load:
            mock_judge_fn = MagicMock(return_value="response")
            mock_load.return_value = mock_judge_fn

            score, prompt, response = wrapped.evaluate_answer(
                question="Q?", answer="A", options=None, gold=None
            )
            assert score == 5

    def test_evaluate_answer_batch(self):
        wrapped = WrappedJudgeLM(
            model="gpt-4",
            templates=MagicMock(return_value=[{"role": "user", "content": "test"}]),
            process_judge_response=MagicMock(side_effect=[3, 4]),
            url="https://api.openai.com/v1",
            api_key="sk-key",
        )

        with patch.object(wrapped, "_lazy_load_client") as mock_load:
            mock_judge_fn = MagicMock(return_value=["resp1", "resp2"])
            mock_load.return_value = mock_judge_fn

            scores, prompts, responses = wrapped.evaluate_answer_batch(
                questions=["Q1?", "Q2?"],
                answers=["A1", "A2"],
                options=[None, None],
                golds=[None, None],
            )
            assert scores == [3, 4]
            assert len(prompts) == 2


class TestGuidelineJudgeMetricInit:
    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_boolean_guideline(self, MockWrapped):
        guideline = {
            "name": "helpful",
            "prompt": "Is it helpful?",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        assert metric.metric_name == "helpful"
        assert metric.higher_is_better is False

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_numeric_guideline(self, MockWrapped):
        guideline = {
            "name": "quality",
            "prompt": "Rate quality",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        assert metric.higher_is_better is True

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_percentage_guideline(self, MockWrapped):
        guideline = {
            "name": "accuracy",
            "prompt": "Rate accuracy",
            "scoring_scale": GuidelineScoringScale.PERCENTAGE,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        assert metric.higher_is_better is True

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_custom_category_guideline(self, MockWrapped):
        guideline = {
            "name": "sentiment",
            "prompt": "Rate sentiment",
            "scoring_scale": GuidelineScoringScale.CUSTOM_CATEGORY,
            "scoring_scale_config": {"categories": ["positive", "negative"]},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        assert metric.higher_is_better is False

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_invalid_scoring_scale(self, MockWrapped):
        guideline = {
            "name": "bad",
            "prompt": "Bad",
            "scoring_scale": "unknown",
            "scoring_scale_config": {},
        }
        with pytest.raises(ValueError, match="Invalid guideline"):
            GuidelineJudgeMetric(
                guideline=guideline, model="gpt-4", url="http://url", api_key="key"
            )


class TestGuidelineJudgeMetricCompute:
    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_compute(self, MockWrapped):
        guideline = {
            "name": "quality",
            "prompt": "Rate quality",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        mock_judge = metric.judge
        mock_judge.evaluate_answer_batch.return_value = (
            [4, 5],
            [["msg1"], ["msg2"]],
            [MagicMock(score=4), MagicMock(score=5)],
        )

        doc1 = MagicMock(query="Q1")
        doc2 = MagicMock(query="Q2")
        resp1 = MagicMock(final_text=["A1"])
        resp2 = MagicMock(final_text=["A2"])

        results = metric.compute(responses=[resp1, resp2], docs=[doc1, doc2])
        assert len(results) == 2
        assert results[0]["quality"] == 4
        assert results[1]["quality"] == 5

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_compute_with_string_judgement(self, MockWrapped):
        guideline = {
            "name": "helpful",
            "prompt": "Is it helpful?",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        metric.judge.evaluate_answer_batch.return_value = (
            ["true"],
            [["msg"]],
            ["some_string_response"],
        )

        doc = MagicMock(query="Q")
        resp = MagicMock(final_text=["A"])

        results = metric.compute(responses=[resp], docs=[doc])
        assert results[0]["helpful"] == "true"
        assert results[0][f"judgement_judge_helpful"] == "some_string_response"


class TestAggregateScores:
    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_numeric_aggregate(self, MockWrapped):
        guideline = {
            "name": "quality",
            "prompt": "Rate",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        result = metric.aggregate_scores([3, 4, 5])
        assert result == 4.0

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_numeric_empty(self, MockWrapped):
        guideline = {
            "name": "quality",
            "prompt": "Rate",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        result = metric.aggregate_scores([])
        assert result == 0.0

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_boolean_aggregate(self, MockWrapped):
        guideline = {
            "name": "helpful",
            "prompt": "Is it helpful?",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        result = metric.aggregate_scores(["true", "false", "true"])
        assert result == {"true": 2, "false": 1}

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_custom_category_aggregate(self, MockWrapped):
        guideline = {
            "name": "sentiment",
            "prompt": "Sentiment",
            "scoring_scale": GuidelineScoringScale.CUSTOM_CATEGORY,
            "scoring_scale_config": {"categories": ["good", "bad"]},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        result = metric.aggregate_scores(["good", "good", "bad"])
        assert result == {"good": 2, "bad": 1}

    @patch("api.evaluations.eval_pipeline.guideline_judge.WrappedJudgeLM")
    def test_percentage_aggregate(self, MockWrapped):
        guideline = {
            "name": "accuracy",
            "prompt": "Rate accuracy",
            "scoring_scale": GuidelineScoringScale.PERCENTAGE,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline, model="gpt-4", url="http://url", api_key="key"
        )
        result = metric.aggregate_scores([80, 90, 100])
        assert result == 90.0
