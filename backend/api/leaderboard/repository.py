from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.datasets.models import Dataset
from api.evaluations.models import Trace


class LeaderboardRepository:
    """Repository for leaderboard database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_leaderboard_traces(self) -> list[Trace]:
        """Get all completed traces that count on leaderboard (across all datasets)."""
        query = (
            select(Trace)
            .where(Trace.status == "completed")
            .where(Trace.count_on_leaderboard == True)
            .order_by(Trace.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_dataset_by_name(self, name: str) -> Dataset | None:
        """Get a dataset by name."""
        query = select(Dataset).where(Dataset.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
