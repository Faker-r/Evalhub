"""Unit tests for guideline schema validation."""

import pytest
from pydantic import ValidationError

from api.guidelines.schemas import (
    BooleanScaleConfig,
    CustomCategoryScaleConfig,
    GuidelineCreate,
    GuidelineScoringScale,
    NumericScaleConfig,
    PercentageScaleConfig,
)


class TestGuidelineScoringScale:
    def test_str_representation(self):
        assert str(GuidelineScoringScale.BOOLEAN) == "boolean"
        assert str(GuidelineScoringScale.NUMERIC) == "numeric"

    def test_repr_representation(self):
        assert repr(GuidelineScoringScale.BOOLEAN) == "boolean"


class TestGuidelineCreateValidation:
    def test_valid_boolean(self):
        g = GuidelineCreate(
            name="test",
            prompt="Is it?",
            category="quality",
            scoring_scale=GuidelineScoringScale.BOOLEAN,
            scoring_scale_config=BooleanScaleConfig(),
        )
        assert g.scoring_scale == GuidelineScoringScale.BOOLEAN

    def test_valid_numeric(self):
        g = GuidelineCreate(
            name="test",
            prompt="Rate",
            category="quality",
            scoring_scale=GuidelineScoringScale.NUMERIC,
            scoring_scale_config=NumericScaleConfig(min_value=1, max_value=5),
        )
        assert g.scoring_scale_config.min_value == 1

    def test_valid_percentage(self):
        g = GuidelineCreate(
            name="test",
            prompt="Score %",
            category="quality",
            scoring_scale=GuidelineScoringScale.PERCENTAGE,
            scoring_scale_config=PercentageScaleConfig(),
        )
        assert g.scoring_scale == GuidelineScoringScale.PERCENTAGE

    def test_valid_custom_category(self):
        g = GuidelineCreate(
            name="test",
            prompt="Pick one",
            category="quality",
            scoring_scale=GuidelineScoringScale.CUSTOM_CATEGORY,
            scoring_scale_config=CustomCategoryScaleConfig(categories=["a", "b"]),
        )
        assert g.scoring_scale_config.categories == ["a", "b"]

    def test_mismatched_boolean_with_numeric_config(self):
        with pytest.raises(ValidationError):
            GuidelineCreate(
                name="test",
                prompt="Is it?",
                category="quality",
                scoring_scale=GuidelineScoringScale.BOOLEAN,
                scoring_scale_config=NumericScaleConfig(min_value=1, max_value=5),
            )

    def test_mismatched_numeric_with_boolean_config(self):
        with pytest.raises(ValidationError):
            GuidelineCreate(
                name="test",
                prompt="Rate",
                category="quality",
                scoring_scale=GuidelineScoringScale.NUMERIC,
                scoring_scale_config=BooleanScaleConfig(),
            )

    def test_mismatched_custom_category_with_boolean_config(self):
        with pytest.raises(ValidationError):
            GuidelineCreate(
                name="test",
                prompt="Pick",
                category="quality",
                scoring_scale=GuidelineScoringScale.CUSTOM_CATEGORY,
                scoring_scale_config=BooleanScaleConfig(),
            )

    def test_mismatched_percentage_with_numeric_config(self):
        with pytest.raises(ValidationError):
            GuidelineCreate(
                name="test",
                prompt="Score %",
                category="quality",
                scoring_scale=GuidelineScoringScale.PERCENTAGE,
                scoring_scale_config=NumericScaleConfig(min_value=0, max_value=100),
            )
