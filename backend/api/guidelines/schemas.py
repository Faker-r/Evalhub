from pydantic import BaseModel, ConfigDict, field_validator
from enum import Enum
from typing import Union


class GuidelineScoringScale(str, Enum):
    """Enum for guideline scoring scales."""

    BOOLEAN = "boolean"
    CUSTOM_CATEGORY = "custom_category"
    NUMERIC = "numeric"
    PERCENTAGE = "percentage"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class BooleanScaleConfig(BaseModel):
    """Config for boolean scoring scale."""

    ...


class CustomCategoryScaleConfig(BaseModel):
    """Config for custom category scoring scale."""

    categories: list[str]


class NumericScaleConfig(BaseModel):
    """Config for numeric scoring scale."""

    min_value: int
    max_value: int


class PercentageScaleConfig(BaseModel):
    """Config for percentage scoring scale."""

    ...


class GuidelineBase(BaseModel):
    """Base guideline schema."""

    name: str
    prompt: str
    category: str
    scoring_scale: GuidelineScoringScale
    scoring_scale_config: Union[
        BooleanScaleConfig,
        CustomCategoryScaleConfig,
        NumericScaleConfig,
        PercentageScaleConfig,
    ]

    @field_validator("scoring_scale_config")
    @classmethod
    def validate_config(cls, v, info):
        scoring_scale = info.data.get("scoring_scale")
        if scoring_scale == GuidelineScoringScale.BOOLEAN and not isinstance(
            v, BooleanScaleConfig
        ):
            raise ValueError("Boolean scale requires BooleanScaleConfig")
        elif scoring_scale == GuidelineScoringScale.CUSTOM_CATEGORY and not isinstance(
            v, CustomCategoryScaleConfig
        ):
            raise ValueError("Custom category scale requires CustomCategoryScaleConfig")
        elif scoring_scale == GuidelineScoringScale.NUMERIC and not isinstance(
            v, NumericScaleConfig
        ):
            raise ValueError("Numeric scale requires NumericScaleConfig")
        elif scoring_scale == GuidelineScoringScale.PERCENTAGE and not isinstance(
            v, PercentageScaleConfig
        ):
            raise ValueError("Percentage scale requires PercentageScaleConfig")
        return v


class GuidelineCreate(GuidelineBase):
    """Guideline creation schema."""

    ...


class GuidelineResponse(BaseModel):
    """Guideline response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    prompt: str
    category: str
    scoring_scale: GuidelineScoringScale
    scoring_scale_config: Union[
        BooleanScaleConfig,
        CustomCategoryScaleConfig,
        NumericScaleConfig,
        PercentageScaleConfig,
    ]


class GuidelineListResponse(BaseModel):
    """Response schema for listing guidelines."""

    guidelines: list[GuidelineResponse]
