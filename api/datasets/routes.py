from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.datasets.schemas import DatasetListResponse, DatasetResponse
from api.datasets.service import DatasetService
from api.users.models import User

logger = get_logger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def add_dataset(
    name: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DatasetResponse:
    """Add a new dataset.

    Upload a JSONL file with one JSON object per line.
    Each line should have an "input" field with the prompt.
    """
    logger.debug(f"Adding dataset: {name} by user {current_user.email}")
    return await DatasetService(session).create_dataset(name, category, file)


@router.get("", response_model=DatasetListResponse)
async def get_datasets(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DatasetListResponse:
    """Get all datasets."""
    logger.debug(f"Getting all datasets for user {current_user.email}")
    datasets = await DatasetService(session).get_all_datasets()
    return DatasetListResponse(datasets=datasets)
