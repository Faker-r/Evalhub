from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import CurrentUser, get_current_user
from api.evaluations.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    TaskEvaluationRequest,
    TaskEvaluationResponse,
    FlexibleEvaluationRequest,
    TraceListResponse,
    TraceResponse,
    TraceSamplesRequest,
    TraceSamplesResponse,
)
from api.evaluations.service import EvaluationService

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def run_evaluation(
    request: EvaluationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> EvaluationResponse:
    """Run an evaluation on a dataset with given guidelines.

    This endpoint:
    1. Generates completions for each sample in the dataset
    2. Judges each completion against each guideline
    3. Returns aggregated scores
    """
    logger.debug(
        f"Running evaluation: dataset={request.dataset_name}, "
        f"guidelines={request.guideline_names}, user={current_user.email}"
    )
    return await EvaluationService(session, current_user.id).run_evaluation(request)


@router.post(
    "/tasks", response_model=TaskEvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def run_task_evaluation(
    request: TaskEvaluationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskEvaluationResponse:
    """Run an evaluation on a task."""
    logger.debug(
        f"Running task evaluation: task={request.task_name}, "
        f"model={request.model_completion_config.model_name}, user={current_user.email}"
    )
    return await EvaluationService(session, current_user.id).run_task_evaluation(
        request
    )


@router.post(
    "/flexible",
    response_model=TaskEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_flexible_evaluation(
    request: FlexibleEvaluationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskEvaluationResponse:
    """Run a flexible evaluation on a dataset with configurable parsing and judging."""
    logger.debug(
        f"Running flexible evaluation: dataset={request.dataset_name}, "
        f"judge_type={request.judge_type}, user={current_user.email}"
    )
    return await EvaluationService(session, current_user.id).run_flexible_evaluation(
        request
    )


@router.get("/traces", response_model=TraceListResponse)
async def get_traces(
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceListResponse:
    """Get all evaluation traces for the current user."""
    logger.debug(f"Getting traces for user {current_user.email}")
    traces = await EvaluationService(session, current_user.id).get_traces()
    return TraceListResponse(traces=traces)


@router.get("/traces/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceResponse:
    """Get a specific evaluation trace."""
    logger.debug(f"Getting trace {trace_id} for user {current_user.email}")
    return await EvaluationService(session, current_user.id).get_trace(trace_id)


@router.get("/traces/{trace_id}/samples", response_model=TraceSamplesResponse)
async def get_trace_samples(
    trace_id: int,
    n_samples: int = 3,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceSamplesResponse:
    """Get samples for a specific trace."""
    logger.debug(f"Getting samples for trace {trace_id} for user {current_user.email}, n_samples={n_samples}")
    request = TraceSamplesRequest(trace_id=trace_id, n_samples=n_samples)
    return await EvaluationService(session, current_user.id).get_trace_samples(request)
