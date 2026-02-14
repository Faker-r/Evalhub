"""User routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import CurrentUser, get_current_user
from api.users.schemas import (
    ApiKeyCreate,
    ApiKeyListResponse,
    ApiKeyResponse,
    UserResponse,
)
from api.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


# ==================== User Endpoints ====================


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse(id=current_user.id, email=current_user.email)


# ==================== API Key Endpoints ====================


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def add_api_key(
    api_key_data: ApiKeyCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiKeyResponse:
    """Add an API key for the current user."""
    logger.debug(
        f"Adding API key for user {current_user.id}, provider_id {api_key_data.provider_id}"
    )
    return await UserService(session).create_api_key(current_user.id, api_key_data)


@router.get("/api-keys", response_model=ApiKeyListResponse)
async def list_api_keys(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiKeyListResponse:
    """List all API key providers for the current user."""
    logger.debug(f"Listing API keys for user {current_user.id}")
    api_keys = await UserService(session).list_api_keys(current_user.id)
    return ApiKeyListResponse(api_key_providers=api_keys)


@router.delete("/api-keys/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete an API key for the current user."""
    logger.debug(
        f"Deleting API key for user {current_user.id}, provider_id {provider_id}"
    )
    await UserService(session).delete_api_key(current_user.id, provider_id)
