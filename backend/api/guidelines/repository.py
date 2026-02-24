from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from api.guidelines.models import Guideline
from api.guidelines.schemas import GuidelineCreate

logger = get_logger(__name__)


class GuidelineRepository:
    """Repository for handling guideline database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, guideline_data: GuidelineCreate, user_id: str) -> Guideline:
        """Create a new guideline.

        Args:
            guideline_data: Guideline creation data
            user_id: ID of the user creating the guideline

        Returns:
            Guideline: Created guideline
        """
        guideline = Guideline(
            name=guideline_data.name,
            prompt=guideline_data.prompt,
            category=guideline_data.category,
            scoring_scale=guideline_data.scoring_scale.value,
            scoring_scale_config=guideline_data.scoring_scale_config.model_dump(),
            visibility=guideline_data.visibility.value,
            user_id=user_id,
        )
        self.session.add(guideline)
        await self.session.commit()
        await self.session.refresh(guideline)

        logger.info(f"Created guideline: {guideline.name} (id={guideline.id})")
        return guideline

    async def get_all(self, user_id: str | None = None) -> list[Guideline]:
        """Get all guidelines visible to the user.

        Args:
            user_id: ID of the user requesting guidelines (None for unauthenticated)

        Returns:
            list[Guideline]: List of visible guidelines
        """
        query = select(Guideline).order_by(Guideline.id.desc())
        
        if user_id:
            query = query.where(
                (Guideline.visibility == "public") | (Guideline.user_id == user_id)
            )
        else:
            query = query.where(Guideline.visibility == "public")
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, guideline_id: int) -> Guideline:
        """Get guideline by ID.

        Args:
            guideline_id: Guideline ID

        Returns:
            Guideline: Found guideline

        Raises:
            NotFoundException: If guideline not found
        """
        query = select(Guideline).where(Guideline.id == guideline_id)
        result = await self.session.execute(query)
        guideline = result.scalar_one_or_none()

        if not guideline:
            raise NotFoundException("Guideline not found")

        return guideline

    async def get_by_name(self, name: str) -> Guideline | None:
        """Get guideline by name.

        Args:
            name: Guideline name

        Returns:
            Guideline | None: Found guideline or None
        """
        query = select(Guideline).where(Guideline.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
