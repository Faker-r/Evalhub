from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MetricScore(BaseModel):
    """Score for a single metric."""

    metric_name: str
    mean: float
    std: float
    failed: int


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""

    model_config = ConfigDict(from_attributes=True)

    trace_id: int
    dataset_name: str
    completion_model: str
    model_provider: str
    judge_model: str
    scores: list[MetricScore]
    total_failures: int
    created_at: datetime


class DatasetLeaderboard(BaseModel):
    """Leaderboard for a single dataset."""

    dataset_name: str
    sample_count: int
    entries: list[LeaderboardEntry]


class LeaderboardResponse(BaseModel):
    """Response schema for the leaderboard endpoint."""

    datasets: list[DatasetLeaderboard]
