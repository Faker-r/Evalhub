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
    session: AsyncSession = Depends(get_session),
) -> LeaderboardResponse:
    """Get the leaderboard for all datasets.

    Returns all completed evaluation runs with count_on_leaderboard=True,
    grouped by dataset name and ranked by average metric scores.

    Each dataset includes:
    - Dataset name and sample count
    - List of entries (traces) ranked by avg_score
    
    Each entry includes:
    - Model name and provider
    - Judge model used
    - Per-metric scores (mean, std, failed)
    - Total failures across all metrics
    - Average score (used for ranking)
    """
    logger.debug("Getting leaderboard for all datasets")
    return await LeaderboardService(session).get_leaderboard()
