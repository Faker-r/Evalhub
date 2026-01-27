from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BenchmarkResponse(BaseModel):
    """Benchmark response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tasks: Optional[list[str]] = None
    dataset_name: str
    hf_repo: str
    description: Optional[str] = None
    author: Optional[str] = None
    downloads: Optional[int] = None
    tags: Optional[list[str]] = None
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

class TaskDetailsResponse(BaseModel):
    """Response schema for task details."""

    task_name: str
    task_details_nested_dict: Optional[dict] = None


class BenchmarkTaskResponse(BaseModel):
    """Response schema for benchmark task (per-task size/tokens)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    benchmark_id: int
    task_name: str
    hf_subset: Optional[str] = None
    evaluation_splits: Optional[list[str]] = None
    dataset_size: Optional[int] = None
    estimated_input_tokens: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class BenchmarkTasksListResponse(BaseModel):
    """Response schema for listing benchmark tasks."""

    tasks: list[BenchmarkTaskResponse]
