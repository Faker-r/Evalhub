from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.security import CurrentUser, get_current_user
from api.evaluation_comparison.schemas import (
    ComparisonRequest,
    OverlappingDatasetsResult,
    SideBySideReportResult,
)
from api.evaluation_comparison.service import EvaluationComparisonService

router = APIRouter(prefix="/evaluation-comparison", tags=["evaluation-comparison"])


@router.post("/overlapping-datasets", response_model=OverlappingDatasetsResult)
async def get_overlapping_datasets(
    request: ComparisonRequest,
    session: AsyncSession = Depends(get_session),
    _current_user: CurrentUser = Depends(get_current_user),
) -> OverlappingDatasetsResult:
    return await EvaluationComparisonService(session).get_overlapping_datasets(
        request.model_provider_pairs
    )


@router.post("/side-by-side-report", response_model=SideBySideReportResult)
async def generate_side_by_side_report(
    request: ComparisonRequest,
    session: AsyncSession = Depends(get_session),
    _current_user: CurrentUser = Depends(get_current_user),
) -> SideBySideReportResult:
    return await EvaluationComparisonService(session).generate_side_by_side_report(
        request.model_provider_pairs
    )
