"""Unit tests for guideline judge scoring scale classes and utility functions."""

import json

import pytest
from pydantic import BaseModel, ValidationError

from api.evaluations.eval_pipeline.guideline_judge import (
    BooleanGuidelineScoringScale,
    BooleanScoreResponse,
    CustomCategoryGuidelineScoringScale,
    GuidelineJudgeMetric,
    NumericGuidelineScoringScale,
    PercentageGuidelineScoringScale,
    PercentageScoreResponse,
    generate_get_judge_prompt_function,
    process_judge_response,
)
from api.guidelines.schemas import GuidelineScoringScale


# ==================== Response Models ====================


class TestBooleanScoreResponse:
    def test_true_value(self):
        r = BooleanScoreResponse(score="true")
        assert r.score == "true"

    def test_false_value(self):
        r = BooleanScoreResponse(score="false")
        assert r.score == "false"

    def test_invalid_value(self):
        with pytest.raises(ValidationError):
            BooleanScoreResponse(score="maybe")


class TestPercentageScoreResponse:
    def test_valid_score(self):
        r = PercentageScoreResponse(score=75)
        assert r.score == 75

    def test_zero_score(self):
        r = PercentageScoreResponse(score=0)
        assert r.score == 0

    def test_max_score(self):
        r = PercentageScoreResponse(score=100)
        assert r.score == 100

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            PercentageScoreResponse(score=-1)

    def test_over_100_rejected(self):
        with pytest.raises(ValidationError):
            PercentageScoreResponse(score=101)


# ==================== Scoring Scale Classes ====================


class TestBooleanGuidelineScoringScale:
    def test_generate_response_class(self):
        scale = BooleanGuidelineScoringScale()
        cls = scale.generate_response_class({})
        assert cls is BooleanScoreResponse

    def test_generate_score_prompt(self):
        scale = BooleanGuidelineScoringScale()
        prompt = scale.generate_score_prompt({})
        assert "true" in prompt.lower()
        assert "false" in prompt.lower()


class TestPercentageGuidelineScoringScale:
    def test_generate_response_class(self):
        scale = PercentageGuidelineScoringScale()
        cls = scale.generate_response_class({})
        assert cls is PercentageScoreResponse

    def test_generate_score_prompt(self):
        scale = PercentageGuidelineScoringScale()
        prompt = scale.generate_score_prompt({})
        assert "0" in prompt
        assert "100" in prompt


class TestNumericGuidelineScoringScale:
    def test_generate_response_class(self):
        scale = NumericGuidelineScoringScale()
        guideline = {"scoring_scale_config": {"min_value": 1, "max_value": 5}}
        cls = scale.generate_response_class(guideline)

        valid = cls(score=3)
        assert valid.score == 3

        with pytest.raises(ValidationError):
            cls(score=0)

        with pytest.raises(ValidationError):
            cls(score=6)

    def test_generate_score_prompt(self):
        scale = NumericGuidelineScoringScale()
        guideline = {"scoring_scale_config": {"min_value": 1, "max_value": 10}}
        prompt = scale.generate_score_prompt(guideline)
        assert "1" in prompt
        assert "10" in prompt


class TestCustomCategoryGuidelineScoringScale:
    def test_generate_response_class(self):
        scale = CustomCategoryGuidelineScoringScale()
        guideline = {
            "scoring_scale_config": {"categories": ["poor", "average", "excellent"]}
        }
        cls = scale.generate_response_class(guideline)

        valid = cls(score="average")
        assert valid.score == "average"

        with pytest.raises(ValidationError):
            cls(score="terrible")

    def test_generate_score_prompt(self):
        scale = CustomCategoryGuidelineScoringScale()
        guideline = {
            "scoring_scale_config": {"categories": ["poor", "average", "excellent"]}
        }
        prompt = scale.generate_score_prompt(guideline)
        assert "poor" in prompt
        assert "average" in prompt
        assert "excellent" in prompt


# ==================== Utility Functions ====================


class TestGenerateGetJudgePromptFunction:
    def test_basic_prompt(self):
        guideline = {
            "prompt": "Is the response helpful?",
            "scoring_scale_config": {},
        }
        scale = BooleanGuidelineScoringScale()
        fn = generate_get_judge_prompt_function(guideline, scale)

        result = fn(question="What is 2+2?", answer="4")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert "Is the response helpful?" in result[0]["content"]
        assert "What is 2+2?" in result[0]["content"]
        assert "4" in result[0]["content"]

    def test_with_gold_answer(self):
        guideline = {"prompt": "Check accuracy", "scoring_scale_config": {}}
        scale = BooleanGuidelineScoringScale()
        fn = generate_get_judge_prompt_function(guideline, scale)

        result = fn(question="Q", answer="A", gold="correct_answer")
        assert "correct_answer" in result[0]["content"]

    def test_without_gold_answer(self):
        guideline = {"prompt": "Check quality", "scoring_scale_config": {}}
        scale = BooleanGuidelineScoringScale()
        fn = generate_get_judge_prompt_function(guideline, scale)

        result = fn(question="Q", answer="A")
        assert "gold answer" not in result[0]["content"].lower()


class TestProcessJudgeResponse:
    def test_pydantic_model_response(self):
        response = BooleanScoreResponse(score="true")
        result = process_judge_response(response)
        assert result == "true"

    def test_percentage_response(self):
        response = PercentageScoreResponse(score=85)
        result = process_judge_response(response)
        assert result == 85

    def test_json_string_response(self):
        response = json.dumps({"score": 42})
        result = process_judge_response(response)
        assert result == 42


# ==================== GuidelineJudgeMetric Init ====================


class TestGuidelineJudgeMetricInit:
    def test_boolean_scale_init(self):
        guideline = {
            "name": "helpfulness",
            "prompt": "Is the response helpful?",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="gpt-4o",
            url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert metric.metric_name == "helpfulness"
        assert metric.higher_is_better is False
        assert isinstance(
            metric.guideline_scoring_scale, BooleanGuidelineScoringScale
        )

    def test_numeric_scale_init(self):
        guideline = {
            "name": "quality",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
            "prompt": "Rate quality",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="gpt-4o",
            url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert metric.higher_is_better is True

    def test_percentage_scale_init(self):
        guideline = {
            "name": "accuracy",
            "scoring_scale": GuidelineScoringScale.PERCENTAGE,
            "scoring_scale_config": {},
            "prompt": "Rate accuracy",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="gpt-4o",
            url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert metric.higher_is_better is True

    def test_custom_category_scale_init(self):
        guideline = {
            "name": "sentiment",
            "scoring_scale": GuidelineScoringScale.CUSTOM_CATEGORY,
            "scoring_scale_config": {"categories": ["positive", "negative"]},
            "prompt": "Classify sentiment",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="gpt-4o",
            url="https://api.openai.com/v1",
            api_key="sk-test",
        )
        assert metric.higher_is_better is False

    def test_invalid_scale_raises(self):
        guideline = {
            "name": "bad",
            "scoring_scale": "nonexistent",
            "scoring_scale_config": {},
            "prompt": "test",
        }
        with pytest.raises(ValueError, match="Invalid guideline"):
            GuidelineJudgeMetric(
                guideline=guideline,
                model="gpt-4o",
                url="https://api.openai.com/v1",
                api_key="sk-test",
            )

    def test_extra_body_passed(self):
        guideline = {
            "name": "test",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
            "prompt": "test",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="gpt-4o",
            url="https://api.openai.com/v1",
            api_key="sk-test",
            extra_body={"custom_param": "value"},
        )
        assert metric.judge.extra_body == {"custom_param": "value"}


class TestAggregateScores:
    def test_numeric_aggregation(self):
        guideline = {
            "name": "q",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
            "prompt": "test",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="m",
            url="http://test",
            api_key="k",
        )
        result = metric.aggregate_scores([3.0, 4.0, 5.0])
        assert result == 4.0

    def test_numeric_empty(self):
        guideline = {
            "name": "q",
            "scoring_scale": GuidelineScoringScale.NUMERIC,
            "scoring_scale_config": {"min_value": 1, "max_value": 5},
            "prompt": "test",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="m",
            url="http://test",
            api_key="k",
        )
        result = metric.aggregate_scores([])
        assert result == 0.0

    def test_boolean_aggregation(self):
        guideline = {
            "name": "q",
            "scoring_scale": GuidelineScoringScale.BOOLEAN,
            "scoring_scale_config": {},
            "prompt": "test",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="m",
            url="http://test",
            api_key="k",
        )
        result = metric.aggregate_scores(["true", "true", "false"])
        assert result == {"true": 2, "false": 1}

    def test_custom_category_aggregation(self):
        guideline = {
            "name": "q",
            "scoring_scale": GuidelineScoringScale.CUSTOM_CATEGORY,
            "scoring_scale_config": {"categories": ["good", "bad"]},
            "prompt": "test",
        }
        metric = GuidelineJudgeMetric(
            guideline=guideline,
            model="m",
            url="http://test",
            api_key="k",
        )
        result = metric.aggregate_scores(["good", "good", "bad"])
        assert result == {"good": 2, "bad": 1}
