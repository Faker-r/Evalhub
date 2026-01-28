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

    async def create(self, guideline_data: GuidelineCreate) -> Guideline:
        """Create a new guideline.

        Args:
            guideline_data: Guideline creation data

        Returns:
            Guideline: Created guideline
        """
        guideline = Guideline(
            name=guideline_data.name,
            prompt=guideline_data.prompt,
            category=guideline_data.category,
            scoring_scale=guideline_data.scoring_scale.value,
            scoring_scale_config=guideline_data.scoring_scale_config.model_dump(),
        )
        self.session.add(guideline)
        await self.session.commit()
        await self.session.refresh(guideline)

        logger.info(f"Created guideline: {guideline.name} (id={guideline.id})")
        return guideline

    async def get_all(self) -> list[Guideline]:
        """Get all guidelines.

        Returns:
            list[Guideline]: List of all guidelines
        """
        query = select(Guideline).order_by(Guideline.id.desc())
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
