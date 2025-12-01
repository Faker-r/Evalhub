from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRequest(BaseModel):
    """Request schema for running an evaluation."""

    dataset_name: str
    guideline_names: list[str]
    completion_model: str
    model_provider: str = "openai"
    api_base: str | None = None  # Optional, defaults to provider's default
    judge_model: str = "gpt-3.5-turbo"


class ScoreDistribution(BaseModel):
    """Score distribution for a guideline."""

    mean: float
    distribution: dict[str, int]  # {"1": 5, "2": 10, ...}
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
    scores: dict[str, ScoreDistribution]
    created_at: datetime


class TraceResponse(BaseModel):
    """Response schema for a trace."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
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

