from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.leaderboard.schemas import LeaderboardResponse
from api.leaderboard.service import LeaderboardService

logger = get_logger(__name__)

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    dataset_name: str,
    session: AsyncSession = Depends(get_session),
) -> LeaderboardResponse:
    """Get the leaderboard for a dataset.

    Returns all completed evaluation runs for the specified dataset,
    ranked by normalized average scores across all guidelines.

    Each entry includes:
    - Model name and provider
    - Judge model used
    - Per-guideline scores (raw mean, max_score, normalized)
    - Total failures across all guidelines
    - Normalized average score (used for ranking)
    """
    logger.debug(f"Getting leaderboard for dataset: {dataset_name}")
    return await LeaderboardService(session).get_leaderboard(dataset_name)
