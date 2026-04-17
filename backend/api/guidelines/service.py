from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.guidelines.models import Guideline
from api.guidelines.repository import GuidelineRepository
from api.guidelines.schemas import GuidelineCreate

logger = get_logger(__name__)


class GuidelineService:
    """Service for handling guideline business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = GuidelineRepository(session)

    async def create_guideline(
        self, guideline_data: GuidelineCreate, user_id: str
    ) -> Guideline:
        """Create a new guideline.

        Args:
            guideline_data: Guideline creation data
            user_id: ID of the user creating the guideline

        Returns:
            Guideline: Created guideline
        """
        # Check for duplicate name before creating
        existing = await self.repository.get_by_name(guideline_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Guideline with name '{guideline_data.name}' already exists",
            )

        return await self.repository.create(guideline_data, user_id)

    def _check_access(self, guideline: Guideline, user_id: str | None) -> bool:
        """Check if user has access to the guideline.

        Args:
            guideline: Guideline to check access for
            user_id: ID of the user requesting access (None for unauthenticated)

        Returns:
            bool: True if user has access, False otherwise
        """
        if guideline.visibility == "public":
            return True
        return user_id is not None and guideline.user_id == user_id

    async def get_all_guidelines(self, user_id: str | None = None) -> list[Guideline]:
        """Get all guidelines visible to the user.

        Args:
            user_id: ID of the user requesting guidelines (None for unauthenticated)

        Returns:
            list[Guideline]: List of visible guidelines
        """
        return await self.repository.get_all(user_id)

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
