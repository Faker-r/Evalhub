"""Repository for handling benchmark database operations."""
import functools
from dataclasses import asdict
from typing import Callable, Optional

from sqlalchemy import func, select, String, cast
from sqlalchemy.ext.asyncio import AsyncSession

from api.benchmarks.models import Benchmark
from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from scripts.benchmark_utils import normalize_language_code

from lighteval.tasks.registry import Registry
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.metrics.utils.metric_utils import Metric

logger = get_logger(__name__)


class BenchmarkRepository:
    """Repository for handling benchmark database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, benchmark_data: dict) -> Benchmark:
        """Create a new benchmark record.

        Args:
            benchmark_data: Dictionary containing benchmark data

        Returns:
            Benchmark: Created benchmark
        """
        benchmark = Benchmark(**benchmark_data)
        self.session.add(benchmark)
        await self.session.commit()
        await self.session.refresh(benchmark)

        logger.info(f"Created benchmark: {benchmark.dataset_name} (id={benchmark.id})")
        return benchmark

    async def update(self, benchmark_id: int, update_data: dict) -> Benchmark:
        """Update an existing benchmark.

        Args:
            benchmark_id: Benchmark ID
            update_data: Dictionary containing fields to update

        Returns:
            Benchmark: Updated benchmark

        Raises:
            NotFoundException: If benchmark not found
        """
        benchmark = await self.get_by_id(benchmark_id)
        for key, value in update_data.items():
            setattr(benchmark, key, value)
        
        await self.session.commit()
        await self.session.refresh(benchmark)

        logger.info(f"Updated benchmark: {benchmark.dataset_name} (id={benchmark.id})")
        return benchmark

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "task_name",
        sort_order: str = "asc",
        tag_filter: Optional[list[str]] = None,
        author_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> tuple[list[Benchmark], int]:
        """Get all benchmarks with filtering, sorting, and pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            tag_filter: Filter by tags (AND logic)
            author_filter: Filter by author
            search_query: Search in task_name, dataset_name, or hf_repo

        Returns:
            tuple[list[Benchmark], int]: List of benchmarks and total count
        """
        query = select(Benchmark)

        # Apply filters
        if tag_filter:
            for tag in tag_filter:
                query = query.where(Benchmark.tags.contains([tag]))
        
        if author_filter:
            query = query.where(Benchmark.author == author_filter)
        
        if search_query:
            # Check if search query matches a language name and convert to language code
            search_lower = search_query.lower().strip()
            normalized_code = normalize_language_code(search_lower)
            
            if normalized_code:
                # Search for the language code in tags
                search_pattern = f"%language:{normalized_code}%"
            else:
                # Regular search pattern
                search_pattern = f"%{search_query}%"
            
            query = query.where(
                (Benchmark.task_name.ilike(search_pattern)) |
                (Benchmark.dataset_name.ilike(search_pattern)) |
                (Benchmark.hf_repo.ilike(search_pattern)) |
                (cast(Benchmark.tags, String).ilike(search_pattern))
            )

        # Build count query with same filters for efficiency
        count_query = select(func.count(Benchmark.id))
        
        # Apply same filters as main query
        if tag_filter:
            for tag in tag_filter:
                count_query = count_query.where(Benchmark.tags.contains([tag]))
        
        if author_filter:
            count_query = count_query.where(Benchmark.author == author_filter)
        
        if search_query:
            # Check if search query matches a language name and convert to language code
            search_lower = search_query.lower().strip()
            normalized_code = normalize_language_code(search_lower)
            
            if normalized_code:
                # Search for the language code in tags
                search_pattern = f"%language:{normalized_code}%"
            else:
                # Regular search pattern
                search_pattern = f"%{search_query}%"
            
            count_query = count_query.where(
                (Benchmark.task_name.ilike(search_pattern)) |
                (Benchmark.dataset_name.ilike(search_pattern)) |
                (Benchmark.hf_repo.ilike(search_pattern)) |
                (cast(Benchmark.tags, String).ilike(search_pattern))
            )
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        sort_column = getattr(Benchmark, sort_by, Benchmark.dataset_name)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        benchmarks = list(result.scalars().all())

        return benchmarks, total

    async def get_by_id(self, benchmark_id: int) -> Benchmark:
        """Get benchmark by ID.

        Args:
            benchmark_id: Benchmark ID

        Returns:
            Benchmark: Found benchmark

        Raises:
            NotFoundException: If benchmark not found
        """
        query = select(Benchmark).where(Benchmark.id == benchmark_id)
        result = await self.session.execute(query)
        benchmark = result.scalar_one_or_none()

        if not benchmark:
            raise NotFoundException("Benchmark not found")

        return benchmark

    async def get_by_dataset_name(self, dataset_name: str) -> Benchmark | None:
        """Get benchmark by dataset name.

        Args:
            dataset_name: Dataset name

        Returns:
            Benchmark | None: Found benchmark or None
        """
        query = select(Benchmark).where(Benchmark.dataset_name == dataset_name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert(self, dataset_name: str, benchmark_data: dict) -> Benchmark:
        """Create or update a benchmark by dataset name.

        Args:
            dataset_name: Dataset name
            benchmark_data: Dictionary containing benchmark data

        Returns:
            Benchmark: Created or updated benchmark
        """
        existing = await self.get_by_dataset_name(dataset_name)
        if existing:
            return await self.update(existing.id, benchmark_data)
        else:
            benchmark_data["dataset_name"] = dataset_name
            return await self.create(benchmark_data)

    def _generate_task_details_dict(self, task_obj: LightevalTaskConfig) -> dict:
        def convert(value):
            if isinstance(value, functools.partial):
                func_name = getattr(value.func, "__name__", str(value.func))
                return f"partial({func_name}, ...)"
            if isinstance(value, Callable):
                return getattr(value, "__name__", repr(value))
            if isinstance(value, Metric.get_allowed_types_for_metrics()):
                return str(value)
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [convert(item) for item in value]
            return value

        return {k: convert(v) for k, v in asdict(task_obj).items()}

    async def get_task_details(self, task_name: str) -> Optional[dict]:
        """Get task details by task name.

        Args:
            task_name: Task name

        Returns:
            TaskDetails: Found task details
        """
        task_map = Registry().load_tasks()
        task_obj = task_map.get(task_name, None) or task_map.get(f"{task_name}|0", None)
        if not task_obj:
            return None
        
        return self._generate_task_details_dict(task_obj.config)
