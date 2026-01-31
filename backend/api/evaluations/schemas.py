from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


class OutputType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"


class JudgeType(str, Enum):
    LLM_AS_JUDGE = "llm_as_judge"
    F1_SCORE = "f1_score"
    EXACT_MATCH = "exact_match"


class TextOutputConfig(BaseModel):
    gold_answer_field: str | None = None


class MultipleChoiceConfig(BaseModel):
    choices_field: str
    gold_answer_field: str


class CategoricalScoreDistribution(BaseModel):
    """Score distribution for boolean and categorical guidelines."""

    distribution: dict[str, int]  # {"1": 5, "2": 10, ...}
    mode: str | None  # The category with most occurrences
    failed: int = 0


class NumericScoreDistribution(BaseModel):
    """Score distribution for numeric and percentage guidelines."""

    mean: float
    std: float
    failed: int = 0


class EvaluationResponse(BaseModel):
    """Response schema for an evaluation run."""

    model_config = ConfigDict(from_attributes=True)

    trace_id: int
    status: str
    dataset_name: str
    sample_count: int
    guideline_names: list[str]
    completion_model: str
    model_provider: str
    judge_model: str
    scores: dict[str, CategoricalScoreDistribution | NumericScoreDistribution]
    created_at: datetime


class TraceResponse(BaseModel):
    """Response schema for a trace."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str  # Supabase UUID
    dataset_name: str
    guideline_names: list[str]
    completion_model: str
    model_provider: str
    judge_model: str
    status: str
    summary: dict | None
    created_at: datetime


class TraceListResponse(BaseModel):
    """Response schema for listing traces."""

    traces: list[TraceResponse]


class TraceEventResponse(BaseModel):
    """Response schema for a trace event."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    trace_id: int
    event_type: str
    sample_id: str | None
    guideline_name: str | None
    data: dict
    created_at: datetime


class DatasetConfig(BaseModel):
    """Request schema for running a task evaluation."""

    dataset_name: str
    n_samples: int | None = None
    n_fewshots: int | None = None


class ModelConfig(BaseModel):
    """Request schema for running a task evaluation."""

    api_source: Literal["standard", "openrouter"]
    model_name: str
    model_id: int
    api_name: str
    model_provider: str
    model_provider_slug: str
    model_provider_id: int


class EvaluationRequest(BaseModel):
    """Request schema for running an evaluation."""

    dataset_name: str
    guideline_names: list[str]
    model_completion_config: ModelConfig
    judge_config: ModelConfig


class TaskEvaluationRequest(BaseModel):
    """Request schema for running a task evaluation."""

    task_name: str
    dataset_config: DatasetConfig
    model_completion_config: ModelConfig
    judge_config: ModelConfig | None = None


class TaskEvaluationResponse(BaseModel):
    """Response schema for a task evaluation."""

    trace_id: int
    status: str
    task_name: str
    sample_count: int | None = None
    guideline_names: list[str] = []
    completion_model: str
    model_provider: str
    judge_model: str
    created_at: datetime


class FlexibleEvaluationRequest(BaseModel):
    """Request schema for running a flexible evaluation."""

    dataset_name: str
    input_field: str
    output_type: OutputType
    text_config: TextOutputConfig | None = None
    mc_config: MultipleChoiceConfig | None = None
    judge_type: JudgeType
    guideline_names: list[str] | None = None
    model_completion_config: ModelConfig
    judge_config: ModelConfig | None = None
