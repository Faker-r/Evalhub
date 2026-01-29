import json
from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.datasets.models import Dataset
from api.datasets.repository import DatasetRepository

logger = get_logger(__name__)

# Number of lines to validate as a sample
VALIDATION_SAMPLE_SIZE = 100


class DatasetService:
    """Service for handling dataset business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = DatasetRepository(session)
        self.s3 = S3Storage()

    async def create_dataset(
        self, name: str, category: str, file: UploadFile
    ) -> Dataset:
        """Create a new dataset from an uploaded JSONL file.

        Args:
            name: Dataset name
            category: Dataset category
            file: Uploaded JSONL file

        Returns:
            Dataset: Created dataset
        """
        # Read file content
        content = await file.read()

        # Check for duplicate name before creating
        existing = await self.repository.get_by_name(name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Dataset with name '{name}' already exists",
            )

        # Validate and count lines
        sample_count = self._validate_and_count(content)

        # Create dataset in database
        dataset = await self.repository.create_from_file(name, category, sample_count)

        # Upload to S3
        self.s3.upload_dataset_file(dataset.name, BytesIO(content))

        logger.info(f"Created dataset: {dataset.name} with {sample_count} samples")
        return dataset

    def _validate_and_count(self, content: bytes) -> int:
        """Validate JSONL content and count lines.

        Validates the first VALIDATION_SAMPLE_SIZE lines as a sample,
        then counts the rest without full validation.

        Args:
            content: Raw file content

        Returns:
            int: Total number of non-empty lines

        Raises:
            HTTPException: If validation fails
        """
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be UTF-8 encoded",
            )

        lines = text.strip().split("\n")
        sample_count = 0
        validated_count = 0

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            sample_count += 1

            # Validate first N lines as sample
            if validated_count < VALIDATION_SAMPLE_SIZE:
                try:
                    data = json.loads(line)
                    if not isinstance(data, dict):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Line {line_num}: Each line must be a JSON object",
                        )
                    if "input" not in data:
                        pass
                        # raise HTTPException(
                        #     status_code=status.HTTP_400_BAD_REQUEST,
                        #     detail=f"Line {line_num}: Missing required 'input' field",
                        # )
                    validated_count += 1
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Line {line_num}: Invalid JSON - {e}",
                    )

        if sample_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no valid data lines",
            )

        return sample_count

    async def get_all_datasets(self) -> list[Dataset]:
        """Get all datasets.

        Returns:
            list[Dataset]: List of all datasets
        """
        return await self.repository.get_all()

    async def get_dataset(self, dataset_id: int) -> Dataset:
        """Get dataset by ID.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset: Found dataset
        """
        return await self.repository.get_by_id(dataset_id)

    async def get_dataset_by_name(self, name: str) -> Dataset:
        """Get dataset by name.

        Args:
            name: Dataset name

        Returns:
            Dataset: Found dataset

        Raises:
            NotFoundException: If dataset not found
        """
        dataset = await self.repository.get_by_name(name)
        if not dataset:
            raise NotFoundException(f"Dataset not found: {name}")
        return dataset

    async def get_dataset_content(self, dataset_id: int) -> str:
        """Get the JSONL content of a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            str: JSONL content

        Raises:
            NotFoundException: If dataset or file not found
        """
        dataset = await self.repository.get_by_id(dataset_id)

        try:
            return self.s3.download_dataset(dataset.name)
        except FileNotFoundError:
            raise NotFoundException(f"Dataset file not found: {dataset.name}")

    async def get_dataset_preview(self, dataset_id: int) -> list[dict]:
        """Get a preview of the dataset content.

        Args:
            dataset_id: Dataset ID

        Returns:
            list[dict]: List of sample JSON objects
        """
        dataset = await self.repository.get_by_id(dataset_id)

        try:
            content = self.s3.download_dataset(dataset.name)
            lines = content.split("\n")

            preview = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    preview.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

            return preview
        except Exception as e:
            logger.error(f"Failed to load preview for dataset {dataset_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load dataset preview",
            )
