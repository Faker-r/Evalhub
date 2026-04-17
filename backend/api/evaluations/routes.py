from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from api.core.config import settings
from api.core.database import get_session
from api.core.logging import get_logger
from api.core.ratelimiter import limiter
from api.core.redis_client import get_eval_progress
from api.core.security import CurrentUser, get_current_user
from api.evaluations.schemas import (
    EvaluationModelConfig,
    FlexibleEvaluationRequest,
    StandardEvaluationModelConfig,
    TaskEvaluationRequest,
    TaskEvaluationResponse,
    TraceDetailsResponse,
    TraceListResponse,
    TraceResponse,
    TraceSamplesRequest,
    TraceSamplesResponse,
)
from api.evaluations.service import EvaluationService

logger = get_logger(__name__)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


def _model_log_name(config: EvaluationModelConfig) -> str:
    if isinstance(config, StandardEvaluationModelConfig):
        return config.model.api_name
    return config.model.id


@router.post(
    "/tasks", response_model=TaskEvaluationResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(settings.RATE_LIMIT)
@limiter.limit(settings.EVALUATION_RUN_RATE_LIMIT)
async def run_task_evaluation(
    request: Request,
    body: TaskEvaluationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskEvaluationResponse:
    """Run an evaluation on a task."""
    logger.debug(
        f"Running task evaluation: task={body.task_name}, "
        f"model={_model_log_name(body.model_completion_config)}, user={current_user.email}"
    )
    # TEMPORARY: auto-flag submissions from admin@evalhub.com for the leaderboard.
    if current_user.email == "admin@evalhub.com":
        body.count_on_leaderboard = True
    return await EvaluationService(session, current_user.id).run_task_evaluation(body)


@router.post(
    "/flexible",
    response_model=TaskEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT)
@limiter.limit(settings.EVALUATION_RUN_RATE_LIMIT)
async def run_flexible_evaluation(
    request: Request,
    body: FlexibleEvaluationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TaskEvaluationResponse:
    """Run a flexible evaluation on a dataset with configurable parsing and judging."""
    logger.debug(
        f"Running flexible evaluation: dataset={body.dataset_name}, "
        f"judge_type={body.judge_type}, user={current_user.email}"
    )
    # TEMPORARY: auto-flag submissions from admin@evalhub.com for the leaderboard.
    if current_user.email == "admin@evalhub.com":
        body.count_on_leaderboard = True
    return await EvaluationService(session, current_user.id).run_flexible_evaluation(
        body
    )


@router.get("/traces", response_model=TraceListResponse)
async def get_traces(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceListResponse:
    """Get evaluation traces for the current user."""
    logger.debug(f"Getting traces for user {current_user.email}")
    traces, total, status_counts = await EvaluationService(
        session, current_user.id
    ).get_traces(limit=limit, offset=offset)
    return TraceListResponse(traces=traces, total=total, status_counts=status_counts)


@router.get("/my-models")
async def get_my_models(
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get distinct model/provider pairs the current user has evaluated."""
    models = await EvaluationService(session, current_user.id).get_distinct_models()
    return {"models": models}


@router.get("/traces/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceResponse:
    """Get a specific evaluation trace."""
    logger.debug(f"Getting trace {trace_id} for user {current_user.email}")
    return await EvaluationService(session, current_user.id).get_trace(trace_id)


@router.get("/trace-details/{trace_id}", response_model=TraceDetailsResponse)
async def get_trace_details(
    trace_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceDetailsResponse:
    """Get trace details from the spec event."""
    return await EvaluationService(session, current_user.id).get_trace_details(trace_id)


@router.get("/traces/{trace_id}/samples", response_model=TraceSamplesResponse)
async def get_trace_samples(
    trace_id: int,
    n_samples: int = 3,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> TraceSamplesResponse:
    """Get samples for a specific trace."""
    logger.debug(
        f"Getting samples for trace {trace_id} for user {current_user.email}, n_samples={n_samples}"
    )
    request = TraceSamplesRequest(trace_id=trace_id, n_samples=n_samples)
    return await EvaluationService(session, current_user.id).get_trace_samples(request)


@router.get("/traces/{trace_id}/progress")
async def get_trace_progress(
    trace_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get real-time progress for a running evaluation."""
    progress = await get_eval_progress(trace_id)
    if progress is None:
        return JSONResponse(content=None)
    return progress


@router.get("/traces/{trace_id}/download")
async def download_trace_results(
    trace_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> StreamingResponse:
    """Download evaluation results as a zip archive."""
    import io
    import os
    import zipfile

    from api.core.s3 import S3Storage

    service = EvaluationService(session, current_user.id)
    files, prefix = await service.get_trace_download_files(trace_id)

    s3 = S3Storage()

    def generate_zip():
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for s3_key in files:
                relative_path = os.path.relpath(s3_key, prefix)
                body = s3.get_file_stream(s3_key)
                zf.writestr(relative_path, body.read())
        buf.seek(0)
        yield buf.read()

    filename = f"eval_results_{trace_id}.zip"
    return StreamingResponse(
        generate_zip(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
