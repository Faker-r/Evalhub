"""Models and providers service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.models_and_providers.models import Model, Provider
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

logger = get_logger(__name__)


class ModelsAndProvidersService:
    """Service for managing models and providers."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Provider Methods ====================

    async def create_provider(self, provider_data: ProviderCreate) -> ProviderResponse:
        """Create a new provider.

        Args:
            provider_data: Provider creation data

        Returns:
            ProviderResponse: Created provider

        Raises:
            AlreadyExistsException: If provider with same name already exists
        """
        # Check if provider already exists
        stmt = select(Provider).where(Provider.name == provider_data.name)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise AlreadyExistsException(
                f"Provider with name '{provider_data.name}' already exists"
            )

        provider = Provider(**provider_data.model_dump())
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)

        logger.info(f"Created provider: {provider.name}")
        return ProviderResponse.model_validate(provider)

    async def get_provider(self, provider_id: int) -> ProviderResponse:
        """Get a provider by ID.

        Args:
            provider_id: Provider ID

        Returns:
            ProviderResponse: Provider data

        Raises:
            NotFoundException: If provider not found
        """
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {provider_id} not found")

        return ProviderResponse.model_validate(provider)

    async def get_provider_by_name(self, name: str) -> ProviderResponse:
        """Get a provider by name.

        Args:
            name: Provider name

        Returns:
            ProviderResponse: Provider data

        Raises:
            NotFoundException: If provider not found
        """
        stmt = select(Provider).where(Provider.name == name)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with name '{name}' not found")

        return ProviderResponse.model_validate(provider)

    async def list_providers(
        self, page: int = 1, page_size: int = 50
    ) -> ProviderListResponse:
        """List all providers with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            ProviderListResponse: List of providers with pagination info
        """
        # Get total count
        count_stmt = select(Provider)
        count_result = await self.session.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Get paginated results
        offset = (page - 1) * page_size
        stmt = select(Provider).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        providers = result.scalars().all()

        return ProviderListResponse(
            providers=[ProviderResponse.model_validate(p) for p in providers],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_provider(
        self, provider_id: int, provider_data: ProviderUpdate
    ) -> ProviderResponse:
        """Update a provider.

        Args:
            provider_id: Provider ID
            provider_data: Provider update data

        Returns:
            ProviderResponse: Updated provider

        Raises:
            NotFoundException: If provider not found
            AlreadyExistsException: If new name conflicts with existing provider
        """
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {provider_id} not found")

        # Check for name conflict if name is being updated
        if provider_data.name and provider_data.name != provider.name:
            name_stmt = select(Provider).where(Provider.name == provider_data.name)
            name_result = await self.session.execute(name_stmt)
            existing = name_result.scalar_one_or_none()
            if existing:
                raise AlreadyExistsException(
                    f"Provider with name '{provider_data.name}' already exists"
                )

        # Update fields
        update_data = provider_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(provider, key, value)

        await self.session.commit()
        await self.session.refresh(provider)

        logger.info(f"Updated provider: {provider.name}")
        return ProviderResponse.model_validate(provider)

    async def delete_provider(self, provider_id: int) -> None:
        """Delete a provider.

        Args:
            provider_id: Provider ID

        Raises:
            NotFoundException: If provider not found
        """
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {provider_id} not found")

        await self.session.delete(provider)
        await self.session.commit()

        logger.info(f"Deleted provider: {provider.name}")

    # ==================== Model Methods ====================

    async def create_model(self, model_data: ModelCreate) -> ModelResponse:
        """Create a new model.

        Args:
            model_data: Model creation data

        Returns:
            ModelResponse: Created model

        Raises:
            NotFoundException: If any provider ID not found
        """
        # Verify all providers exist
        providers = []
        for provider_id in model_data.provider_ids:
            stmt = select(Provider).where(Provider.id == provider_id)
            result = await self.session.execute(stmt)
            provider = result.scalar_one_or_none()
            if not provider:
                raise NotFoundException(f"Provider with ID {provider_id} not found")
            providers.append(provider)

        # Create model
        model_dict = model_data.model_dump(exclude={"provider_ids"})
        model = Model(**model_dict)
        model.providers = providers

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model, ["providers"])

        logger.info(f"Created model: {model.display_name}")
        return ModelResponse.model_validate(model)

    async def get_model(self, model_id: int) -> ModelResponse:
        """Get a model by ID.

        Args:
            model_id: Model ID

        Returns:
            ModelResponse: Model data

        Raises:
            NotFoundException: If model not found
        """
        stmt = select(Model).options(selectinload(Model.providers)).where(Model.id == model_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise NotFoundException(f"Model with ID {model_id} not found")

        return ModelResponse.model_validate(model)

    async def list_models(
        self,
        page: int = 1,
        page_size: int = 50,
        provider_id: int | None = None,
    ) -> ModelListResponse:
        """List all models with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            provider_id: Optional filter by provider ID

        Returns:
            ModelListResponse: List of models with pagination info
        """
        # Build base query
        stmt = select(Model).options(selectinload(Model.providers))

        # Filter by provider if specified
        if provider_id is not None:
            # Join with association table to filter
            stmt = stmt.join(Model.providers).where(Provider.id == provider_id)

        # Get total count
        count_result = await self.session.execute(stmt)
        total = len(count_result.scalars().all())

        # Get paginated results
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return ModelListResponse(
            models=[ModelResponse.model_validate(m) for m in models],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_model(self, model_id: int, model_data: ModelUpdate) -> ModelResponse:
        """Update a model.

        Args:
            model_id: Model ID
            model_data: Model update data

        Returns:
            ModelResponse: Updated model

        Raises:
            NotFoundException: If model or any provider not found
        """
        stmt = select(Model).options(selectinload(Model.providers)).where(Model.id == model_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise NotFoundException(f"Model with ID {model_id} not found")

        # Update fields
        update_data = model_data.model_dump(exclude_unset=True, exclude={"provider_ids"})
        for key, value in update_data.items():
            setattr(model, key, value)

        # Update providers if specified
        if model_data.provider_ids is not None:
            providers = []
            for provider_id in model_data.provider_ids:
                provider_stmt = select(Provider).where(Provider.id == provider_id)
                provider_result = await self.session.execute(provider_stmt)
                provider = provider_result.scalar_one_or_none()
                if not provider:
                    raise NotFoundException(f"Provider with ID {provider_id} not found")
                providers.append(provider)
            model.providers = providers

        await self.session.commit()
        await self.session.refresh(model, ["providers"])

        logger.info(f"Updated model: {model.display_name}")
        return ModelResponse.model_validate(model)

    async def delete_model(self, model_id: int) -> None:
        """Delete a model.

        Args:
            model_id: Model ID

        Raises:
            NotFoundException: If model not found
        """
        stmt = select(Model).where(Model.id == model_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise NotFoundException(f"Model with ID {model_id} not found")

        await self.session.delete(model)
        await self.session.commit()

        logger.info(f"Deleted model: {model.display_name}")
