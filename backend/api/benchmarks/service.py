import math
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api.benchmarks.repository import BenchmarkRepository
from api.benchmarks.schemas import (
    BenchmarkListResponse,
    BenchmarkResponse,
    BenchmarkTaskResponse,
    BenchmarkTasksListResponse,
    TaskDetailsResponse,
)
from api.core.logging import get_logger

logger = get_logger(__name__)


class BenchmarkService:
    """Service for handling benchmark business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = BenchmarkRepository(session)

    async def get_all_benchmarks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "downloads",
        sort_order: str = "desc",
        tag_filter: Optional[list[str]] = None,
        author_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> BenchmarkListResponse:
        """Get all benchmarks with filtering, sorting, and pagination.

        Note: This service layer currently acts as a pass-through to the repository
        with response formatting. It's maintained for future business logic additions
        and to keep a consistent service layer pattern across the application.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            tag_filter: Filter by tag
            author_filter: Filter by author
            search_query: Search in dataset_name or hf_repo

        Returns:
            BenchmarkListResponse: Paginated list of benchmarks
        """
        benchmarks, total = await self.repository.get_all(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            tag_filter=tag_filter,
            author_filter=author_filter,
            search_query=search_query,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # Build response with default task info from first task
        benchmark_responses = []
        for b in benchmarks:
            response = BenchmarkResponse.model_validate(b)
            # Populate default values from first task
            if b.tasks_rel:
                first_task = b.tasks_rel[0]
                response.default_dataset_size = first_task.dataset_size
                response.default_estimated_input_tokens = (
                    first_task.estimated_input_tokens
                )
            benchmark_responses.append(response)

        return BenchmarkListResponse(
            benchmarks=benchmark_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_benchmark(self, benchmark_id: int) -> BenchmarkResponse:
        """Get benchmark by ID.

        Args:
            benchmark_id: Benchmark ID

        Returns:
            BenchmarkResponse: Found benchmark
        """
        benchmark = await self.repository.get_by_id(benchmark_id)
        return BenchmarkResponse.model_validate(benchmark)

    async def get_benchmark_by_dataset_name(
        self, dataset_name: str
    ) -> Optional[BenchmarkResponse]:
        """Get benchmark by dataset name.

        Args:
            dataset_name: Dataset name

        Returns:
            BenchmarkResponse | None: Found benchmark or None
        """
        benchmark = await self.repository.get_by_dataset_name(dataset_name)
        if benchmark:
            return BenchmarkResponse.model_validate(benchmark)
        return None

    async def get_task_details(self, task_name: str) -> TaskDetailsResponse:
        """Get task details by task name.

        Args:
            task_name: Task name

        Returns:
            TaskDetailsResponse: Found task details
        """
        response = TaskDetailsResponse(task_name=task_name)
        task_details_nested_dict = await self.repository.get_task_details(task_name)
        if task_details_nested_dict:
            response.task_details_nested_dict = task_details_nested_dict
        return response

    async def get_benchmark_tasks(
        self, benchmark_id: int
    ) -> BenchmarkTasksListResponse:
        """Get all tasks for a benchmark.

        Args:
            benchmark_id: Benchmark ID

        Returns:
            BenchmarkTasksListResponse: List of tasks with size/token info
        """
        tasks = await self.repository.get_tasks_by_benchmark_id(benchmark_id)
        return BenchmarkTasksListResponse(
            tasks=[BenchmarkTaskResponse.model_validate(t) for t in tasks]
        )
