from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ModelProviderPair(BaseModel):
    model: str
    provider: str


class ComparisonRequest(BaseModel):
    model_provider_pairs: list[ModelProviderPair]


class OverlappingDatasetsResult(BaseModel):
    count: int
    dataset_names: list[str]


class SideBySideReportEntry(BaseModel):
    model: str
    provider: str
    dataset_name: str
    metric_name: str
    trace_id: int
    created_at: datetime
    score: Optional[dict | float] = None


class SpecEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trace_id: int
    event_type: str
    sample_id: Optional[str] = None
    guideline_name: Optional[str] = None
    data: dict
    created_at: datetime


class SideBySideReportResult(BaseModel):
    entries: list[SideBySideReportEntry]
    spec_by_trace: dict[int, Optional[SpecEvent]] = {}
