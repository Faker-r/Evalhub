"""Models and providers routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import CurrentUser, get_current_user
from api.models_and_providers.schemas import (
    ModelCreate,
    ModelListResponse,
    ModelResponse,
    ModelUpdate,
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderUpdate,
)
from api.models_and_providers.service import ModelsAndProvidersService

logger = get_logger(__name__)

router = APIRouter(prefix="/models-and-providers", tags=["models-and-providers"])


# ==================== Provider Endpoints ====================


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: ProviderCreate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProviderResponse:
    """Create a new provider.

    Requires authentication.
    """
    logger.debug(f"Creating provider: {provider_data.name}")
    return await ModelsAndProvidersService(session).create_provider(provider_data)


@router.get("/providers", response_model=ProviderListResponse)
async def list_providers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProviderListResponse:
    """List all providers with pagination.

    Requires authentication.
    """
    logger.debug(f"Listing providers: page={page}, page_size={page_size}")
    return await ModelsAndProvidersService(session).list_providers(page, page_size)


@router.get("/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProviderResponse:
    """Get a provider by ID.

    Requires authentication.
    """
    logger.debug(f"Getting provider: {provider_id}")
    return await ModelsAndProvidersService(session).get_provider(provider_id)


@router.get("/providers/by-name/{name}", response_model=ProviderResponse)
async def get_provider_by_name(
    name: str,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProviderResponse:
    """Get a provider by name.

    Requires authentication.
    """
    logger.debug(f"Getting provider by name: {name}")
    return await ModelsAndProvidersService(session).get_provider_by_name(name)


@router.put("/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProviderResponse:
    """Update a provider.

    Requires authentication.
    """
    logger.debug(f"Updating provider: {provider_id}")
    return await ModelsAndProvidersService(session).update_provider(provider_id, provider_data)


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """Delete a provider.

    Requires authentication.
    """
    logger.debug(f"Deleting provider: {provider_id}")
    await ModelsAndProvidersService(session).delete_provider(provider_id)


# ==================== Model Endpoints ====================


@router.post("/models", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: ModelCreate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ModelResponse:
    """Create a new model.

    Requires authentication.
    """
    logger.debug(f"Creating model: {model_data.display_name}")
    return await ModelsAndProvidersService(session).create_model(model_data)


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    provider_id: int | None = Query(None, description="Filter by provider ID"),
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ModelListResponse:
    """List all models with pagination.

    Optionally filter by provider ID.
    Requires authentication.
    """
    logger.debug(f"Listing models: page={page}, page_size={page_size}, provider_id={provider_id}")
    return await ModelsAndProvidersService(session).list_models(page, page_size, provider_id)


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ModelResponse:
    """Get a model by ID.

    Requires authentication.
    """
    logger.debug(f"Getting model: {model_id}")
    return await ModelsAndProvidersService(session).get_model(model_id)


@router.put("/models/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> ModelResponse:
    """Update a model.

    Requires authentication.
    """
    logger.debug(f"Updating model: {model_id}")
    return await ModelsAndProvidersService(session).update_model(model_id, model_data)


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """Delete a model.

    Requires authentication.
    """
    logger.debug(f"Deleting model: {model_id}")
    await ModelsAndProvidersService(session).delete_model(model_id)
