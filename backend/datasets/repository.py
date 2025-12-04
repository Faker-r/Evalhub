from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundException
from backend.core.logging import get_logger
from backend.datasets.models import Dataset

logger = get_logger(__name__)


class DatasetRepository:
    """Repository for handling dataset database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_from_file(
        self, name: str, category: str, sample_count: int
    ) -> Dataset:
        """Create a new dataset record.

        Args:
            name: Dataset name
            category: Dataset category
            sample_count: Number of samples in the dataset

        Returns:
            Dataset: Created dataset
        """
        dataset = Dataset(
            name=name,
            category=category,
            sample_count=sample_count,
        )
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)

        logger.info(f"Created dataset: {dataset.name} (id={dataset.id})")
        return dataset

    async def get_all(self) -> list[Dataset]:
        """Get all datasets.

        Returns:
            list[Dataset]: List of all datasets
        """
        query = select(Dataset).order_by(Dataset.id.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, dataset_id: int) -> Dataset:
        """Get dataset by ID.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset: Found dataset

        Raises:
            NotFoundException: If dataset not found
        """
        query = select(Dataset).where(Dataset.id == dataset_id)
        result = await self.session.execute(query)
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundException("Dataset not found")

        return dataset

    async def get_by_name(self, name: str) -> Optional[Dataset]:
        """Get dataset by name.

        Args:
            name: Dataset name

        Returns:
            Optional[Dataset]: Found dataset or None
        """
        query = select(Dataset).where(Dataset.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
