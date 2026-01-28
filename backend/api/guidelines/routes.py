from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import CurrentUser, get_current_user
from api.guidelines.schemas import (
    GuidelineCreate,
    GuidelineListResponse,
    GuidelineResponse,
)
from api.guidelines.service import GuidelineService

logger = get_logger(__name__)

router = APIRouter(prefix="/guidelines", tags=["guidelines"])


@router.post("", response_model=GuidelineResponse, status_code=status.HTTP_201_CREATED)
async def add_guideline(
    guideline_data: GuidelineCreate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> GuidelineResponse:
    """Add a new guideline."""
    logger.debug(
        f"Adding guideline: {guideline_data.name} by user {current_user.email}"
    )
    return await GuidelineService(session).create_guideline(guideline_data)


@router.get("", response_model=GuidelineListResponse)
async def get_guidelines(
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> GuidelineListResponse:
    """Get all guidelines."""
    logger.debug(f"Getting all guidelines for user {current_user.email}")
    guidelines = await GuidelineService(session).get_all_guidelines()
    return GuidelineListResponse(guidelines=guidelines)
