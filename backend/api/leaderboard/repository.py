from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.datasets.models import Dataset
from api.evaluations.models import Trace
from api.guidelines.models import Guideline


class LeaderboardRepository:
    """Repository for leaderboard database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_completed_traces_by_dataset(self, dataset_name: str) -> list[Trace]:
        """Get all completed traces for a dataset (across all users) that count on leaderboard."""
        query = (
            select(Trace)
            .where(Trace.dataset_name == dataset_name)
            .where(Trace.status == "completed")
            .where(Trace.count_on_leaderboard == True)
            .order_by(Trace.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_guidelines_by_names(self, names: list[str]) -> dict[str, Guideline]:
        """Get guidelines by their names, returns a dict keyed by name."""
        if not names:
            return {}
        query = select(Guideline).where(Guideline.name.in_(names))
        result = await self.session.execute(query)
        guidelines = result.scalars().all()
        return {g.name: g for g in guidelines}

    async def get_dataset_by_name(self, name: str) -> Dataset | None:
        """Get a dataset by name."""
        query = select(Dataset).where(Dataset.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
