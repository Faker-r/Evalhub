from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GuidelineScore(BaseModel):
    """Score for a single guideline."""

    guideline_name: str
    mean: float
    max_score: int
    normalized: float  # mean / max_score
    failed: int


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""

    model_config = ConfigDict(from_attributes=True)

    trace_id: int
    completion_model: str
    model_provider: str
    judge_model: str
    scores: list[GuidelineScore]
    total_failures: int
    normalized_avg_score: float  # Average of all normalized scores
    created_at: datetime


class LeaderboardResponse(BaseModel):
    """Response schema for the leaderboard endpoint."""

    dataset_name: str
    sample_count: int
    entries: list[LeaderboardEntry]

