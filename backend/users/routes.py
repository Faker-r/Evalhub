from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.logging import get_logger
from backend.core.security import get_current_user
from backend.users.models import User
from backend.users.schemas import (
    ApiKeyCreate,
    ApiKeyListResponse,
    ApiKeyResponse,
    UserResponse,
)
from backend.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


# ==================== User Endpoints ====================


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user."""
    return current_user


# ==================== API Key Endpoints ====================


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def add_api_key(
    api_key_data: ApiKeyCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiKeyResponse:
    """Add an API key for the current user."""
    logger.debug(f"Adding API key for user {current_user.id}, provider {api_key_data.provider}")
    UserService(session).create_api_key(current_user.id, api_key_data)
    return ApiKeyResponse(provider=api_key_data.provider)


@router.get("/api-keys", response_model=ApiKeyListResponse)
async def list_api_keys(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiKeyListResponse:
    """List all API key providers for the current user."""
    logger.debug(f"Listing API keys for user {current_user.id}")
    providers = UserService(session).list_api_keys(current_user.id)
    return ApiKeyListResponse(api_key_providers=[ApiKeyResponse(provider=p) for p in providers])


@router.delete("/api-keys/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an API key for the current user."""
    logger.debug(f"Deleting API key for user {current_user.id}, provider {provider}")
    UserService(session).delete_api_key(current_user.id, provider)
