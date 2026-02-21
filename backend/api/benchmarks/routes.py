from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.benchmarks.schemas import (
    BenchmarkListResponse,
    BenchmarkPreviewResponse,
    BenchmarkResponse,
    BenchmarkTasksListResponse,
    TaskDetailsResponse,
)
from api.benchmarks.service import BenchmarkService
from api.core.database import get_session
from api.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("", response_model=BenchmarkListResponse)
async def get_benchmarks(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    sort_by: str = Query("downloads", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    tag: list[str] | None = Query(
        None, description="Filter by tag (supports multiple)"
    ),
    author: str | None = Query(None, description="Filter by author"),
    search: str | None = Query(None, description="Search in dataset_name or hf_repo"),
    session: AsyncSession = Depends(get_session),
) -> BenchmarkListResponse:
    """Get all benchmarks with filtering, sorting, and pagination.

    - **page**: Page number (1-indexed)
    - **page_size**: Number of items per page (1-100)
    - **sort_by**: Field to sort by (e.g., dataset_name, downloads, estimated_input_tokens)
    - **sort_order**: Sort order (asc or desc)
    - **tag**: Filter by tag
    - **author**: Filter by author
    - **search**: Search in dataset_name or hf_repo
    """
    logger.debug(
        f"Getting benchmarks: page={page}, page_size={page_size}, sort_by={sort_by}"
    )
    return await BenchmarkService(session).get_all_benchmarks(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        tag_filter=tag,
        author_filter=author,
        search_query=search,
    )


@router.get("/task-details/{task_name}", response_model=TaskDetailsResponse)
async def get_task_details(
    task_name: str,
    session: AsyncSession = Depends(get_session),
) -> TaskDetailsResponse:
    """Get task details by task name."""
    logger.debug(f"Getting task details: {task_name}")
    return await BenchmarkService(session).get_task_details(task_name)


@router.get("/{benchmark_id}", response_model=BenchmarkResponse)
async def get_benchmark(
    benchmark_id: int,
    session: AsyncSession = Depends(get_session),
) -> BenchmarkResponse:
    """Get a single benchmark by ID."""
    logger.debug(f"Getting benchmark: {benchmark_id}")
    return await BenchmarkService(session).get_benchmark(benchmark_id)


@router.get("/{benchmark_id}/tasks", response_model=BenchmarkTasksListResponse)
async def get_benchmark_tasks(
    benchmark_id: int,
    session: AsyncSession = Depends(get_session),
) -> BenchmarkTasksListResponse:
    """Get all tasks for a benchmark with size and token information."""
    logger.debug(f"Getting tasks for benchmark: {benchmark_id}")
    return await BenchmarkService(session).get_benchmark_tasks(benchmark_id)


@router.get("/{benchmark_id}/preview", response_model=BenchmarkPreviewResponse)
async def get_benchmark_preview(
    benchmark_id: int,
    num_samples: int = Query(10, ge=1, le=50, description="Number of samples to return"),
    session: AsyncSession = Depends(get_session),
) -> BenchmarkPreviewResponse:
    """Get a preview of benchmark data from HuggingFace.

    Streams data from HuggingFace to avoid downloading the entire dataset.
    Returns the first `num_samples` rows from the dataset.
    """
    logger.debug(f"Getting preview for benchmark: {benchmark_id}")
    return await BenchmarkService(session).get_benchmark_preview(benchmark_id, num_samples)
