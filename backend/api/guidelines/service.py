from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.guidelines.models import Guideline
from api.guidelines.repository import GuidelineRepository
from api.guidelines.schemas import GuidelineCreate
from fastapi import HTTPException, status

logger = get_logger(__name__)


class GuidelineService:
    """Service for handling guideline business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = GuidelineRepository(session)

    async def create_guideline(self, guideline_data: GuidelineCreate) -> Guideline:
        """Create a new guideline.

        Args:
            guideline_data: Guideline creation data

        Returns:
            Guideline: Created guideline
        """
        # Validate prompt contains exactly one {completion} placeholder
        completion_count = guideline_data.prompt.count("{completion}")
        if completion_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Guideline prompt must contain exactly one {completion} placeholder",
            )
        if completion_count > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Guideline prompt contains {completion_count} {{completion}} placeholders, expected exactly 1",
            )

        # Check for duplicate name before creating
        existing = await self.repository.get_by_name(guideline_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Guideline with name '{guideline_data.name}' already exists",
            )

        return await self.repository.create(guideline_data)

    async def get_all_guidelines(self) -> list[Guideline]:
        """Get all guidelines.

        Returns:
            list[Guideline]: List of all guidelines
        """
        return await self.repository.get_all()

    async def get_guideline(self, guideline_id: int) -> Guideline:
        """Get guideline by ID.

        Args:
            guideline_id: Guideline ID

        Returns:
            Guideline: Found guideline
        """
        return await self.repository.get_by_id(guideline_id)

    async def get_guideline_by_name(self, name: str) -> Guideline:
        """Get guideline by name.

        Args:
            name: Guideline name

        Returns:
            Guideline: Found guideline

        Raises:
            HTTPException: If guideline not found
        """
        guideline = await self.repository.get_by_name(name)
        if not guideline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Guideline not found: {name}",
            )
        return guideline
