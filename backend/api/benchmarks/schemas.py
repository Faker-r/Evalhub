from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BenchmarkResponse(BaseModel):
    """Benchmark response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_name: str
    dataset_name: str
    hf_repo: str
    description: Optional[str] = None
    author: Optional[str] = None
    downloads: Optional[int] = None
    tags: Optional[list[str]] = None
    estimated_input_tokens: Optional[int] = None
    repo_type: Optional[str] = None
    created_at_hf: Optional[datetime] = None
    private: Optional[bool] = None
    gated: Optional[bool] = None
    files: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime


class BenchmarkListResponse(BaseModel):
    """Response schema for listing benchmarks with pagination."""

    benchmarks: list[BenchmarkResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
