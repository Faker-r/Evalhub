"""Models and providers service."""

import asyncio
from urllib.parse import quote

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.cache import cache_response
from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.models_and_providers.models import Model, Provider
from api.models_and_providers.schemas import (
    ModelCreate,
    ModelListResponse,
    ModelResponse,
    ModelUpdate,
    OpenRouterModelBase,
    OpenRouterModelEndpointsApiResponse,
    OpenRouterModelListResponse,
    OpenRouterModelsApiResponse,
    OpenRouterProviderApiModel,
    OpenRouterProviderListResponse,
    OpenRouterProvidersApiResponse,
    OpenRouterProvidersByModelResponse,
    OpenRouterProviderResponse,
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderUpdate,
)

logger = get_logger(__name__)
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_TIMEOUT_SECONDS = 30.0
OPENROUTER_MODELS_CACHE_TTL_SECONDS = 300
OPENROUTER_PROVIDERS_CACHE_TTL_SECONDS = 300
OPENROUTER_ENDPOINTS_CACHE_TTL_SECONDS = 300
OPENROUTER_PROVIDER_MODEL_MAP_CACHE_TTL_SECONDS = 300


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
        stmt = (
            select(Model)
            .options(selectinload(Model.providers))
            .where(Model.id == model_id)
        )
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

    async def update_model(
        self, model_id: int, model_data: ModelUpdate
    ) -> ModelResponse:
        """Update a model.

        Args:
            model_id: Model ID
            model_data: Model update data

        Returns:
            ModelResponse: Updated model

        Raises:
            NotFoundException: If model or any provider not found
        """
        stmt = (
            select(Model)
            .options(selectinload(Model.providers))
            .where(Model.id == model_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise NotFoundException(f"Model with ID {model_id} not found")

        # Update fields
        update_data = model_data.model_dump(
            exclude_unset=True, exclude={"provider_ids"}
        )
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

    # ==================== OpenRouter Methods ====================

    @cache_response(
        key_generator=lambda self: "openrouter:models-base",
        ttl=OPENROUTER_MODELS_CACHE_TTL_SECONDS,
        revive=OpenRouterModelListResponse,
    )
    async def _get_openrouter_models_base(self) -> OpenRouterModelListResponse:
        """Get raw OpenRouter model payload."""
        json = await self._fetch_openrouter_json("/models")
        parsed = OpenRouterModelsApiResponse.model_validate(json)
        return OpenRouterModelListResponse(models=parsed.data, total=len(parsed.data))

    async def get_openrouter_models(
        self,
        limit: int = 50,
        offset: int = 0,
        provider_slug: str | None = None,
        search: str | None = None,
        sort: str = "name",
    ) -> OpenRouterModelListResponse:
        """Get OpenRouter models with provider slug mappings, paginated."""
        models_response = await self._get_openrouter_models_base()
        provider_slugs_by_model_id = await self._get_openrouter_provider_slugs_by_model_id()

        models = []
        for model in models_response.models:
            model_dict = model.model_dump()
            model_dict["provider_slugs"] = provider_slugs_by_model_id.get(model.id, [])
            models.append(OpenRouterModelBase.model_validate(model_dict))

        if provider_slug:
            models = [m for m in models if provider_slug in (m.provider_slugs or [])]
        if search:
            q = search.strip().lower()
            if q:
                models = [
                    m
                    for m in models
                    if q in (m.name or "").lower()
                    or q in (m.id or "").lower()
                    or q in (m.description or "").lower()
                ]

        def _context_len(m: OpenRouterModelBase) -> int:
            top = (m.top_provider or {}) if isinstance(m.top_provider, dict) else {}
            ctx = top.get("context_length") or m.context_length
            if isinstance(ctx, (int, float)):
                return int(ctx)
            if isinstance(ctx, str):
                try:
                    return int(ctx)
                except ValueError:
                    return 0
            return 0

        def _price(m: OpenRouterModelBase, key: str) -> float:
            p = m.pricing or {}
            v = p.get(key)
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, str):
                try:
                    return float(v)
                except ValueError:
                    return float("inf")
            return float("inf")

        if sort == "context":
            models.sort(key=lambda m: -_context_len(m))
        elif sort == "input":
            models.sort(key=lambda m: _price(m, "prompt"))
        elif sort == "output":
            models.sort(key=lambda m: _price(m, "completion"))
        else:
            models.sort(key=lambda m: (m.name or "").lower())
        total = len(models)
        page = models[offset : offset + limit]
        return OpenRouterModelListResponse(models=page, total=total)

    @cache_response(
        key_generator=lambda self: "openrouter:providers",
        ttl=OPENROUTER_PROVIDERS_CACHE_TTL_SECONDS,
        revive=OpenRouterProvidersApiResponse,
    )
    async def _get_openrouter_providers_api_response(
        self,
    ) -> OpenRouterProvidersApiResponse:
        """Get typed OpenRouter upstream provider payload."""
        json = await self._fetch_openrouter_json("/providers")
        return OpenRouterProvidersApiResponse.model_validate(json)

    @cache_response(
        key_generator=lambda self: "openrouter:providers-by-model-map",
        ttl=OPENROUTER_PROVIDER_MODEL_MAP_CACHE_TTL_SECONDS,
    )
    async def _get_openrouter_hosted_models_by_provider_slug(
        self,
    ) -> dict[str, list[dict]]:
        """Build provider slug -> hosted model list from OpenRouter model endpoints."""
        providers_response = await self._get_openrouter_providers_api_response()
        models_response = await self._get_openrouter_models_base()

        def normalize(value: str) -> str:
            return "".join(ch for ch in value.lower() if ch.isalnum())

        slug_by_normalized_name: dict[str, str] = {}
        for provider in providers_response.data:
            slug_by_normalized_name[normalize(provider.name)] = provider.slug
            slug_by_normalized_name[normalize(provider.slug)] = provider.slug

        model_ids_by_provider_slug: dict[str, set[str]] = {}

        providers_by_model_tasks = [
            self.get_openrouter_providers_by_model(model.id)
            for model in models_response.models
        ]
        providers_by_model_results = await asyncio.gather(
            *providers_by_model_tasks, return_exceptions=True
        )

        for model, result in zip(
            models_response.models, providers_by_model_results, strict=False
        ):
            if isinstance(result, Exception):
                logger.warning(f"Failed to fetch providers for model '{model.id}': {result}")
                continue
            for provider_name in result.providers:
                provider_slug = slug_by_normalized_name.get(normalize(provider_name))
                if not provider_slug:
                    continue
                (model_ids_by_provider_slug.setdefault(provider_slug, set())).add(
                    model.id
                )

        model_by_id = {model.id: model for model in models_response.models}
        models_by_provider_slug: dict[str, list[dict]] = {}
        for provider_slug, model_ids in model_ids_by_provider_slug.items():
            models_by_provider_slug[provider_slug] = [
                model_by_id[model_id].model_dump()
                for model_id in model_ids
                if model_id in model_by_id
            ]

        return models_by_provider_slug

    @cache_response(
        key_generator=lambda self: "openrouter:provider-slugs-by-model-id",
        ttl=OPENROUTER_PROVIDER_MODEL_MAP_CACHE_TTL_SECONDS,
    )
    async def _get_openrouter_provider_slugs_by_model_id(self) -> dict[str, list[str]]:
        """Build model id -> provider slugs from hosted-model mapping."""
        hosted_models_by_provider_slug = (
            await self._get_openrouter_hosted_models_by_provider_slug()
        )
        slugs_by_model_id: dict[str, set[str]] = {}
        for provider_slug, models in hosted_models_by_provider_slug.items():
            for model in models:
                model_id = model.get("id")
                if not model_id:
                    continue
                slugs_by_model_id.setdefault(model_id, set()).add(provider_slug)
        return {
            model_id: sorted(provider_slugs)
            for model_id, provider_slugs in slugs_by_model_id.items()
        }

    async def get_openrouter_providers(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
        sort: str = "models",
    ) -> OpenRouterProviderListResponse:
        """Get OpenRouter providers with hosted model counts, paginated."""
        providers_response = await self._get_openrouter_providers_api_response()
        hosted_models_by_provider_slug = (
            await self._get_openrouter_hosted_models_by_provider_slug()
        )

        providers = [
            OpenRouterProviderResponse(
                name=provider.name,
                slug=provider.slug,
                model_count=len(hosted_models_by_provider_slug.get(provider.slug, [])),
                privacy_policy_url=provider.privacy_policy_url,
                terms_of_service_url=provider.terms_of_service_url,
                status_page_url=provider.status_page_url,
            )
            for provider in providers_response.data
            if len(hosted_models_by_provider_slug.get(provider.slug, [])) > 0
        ]
        if sort == "name":
            providers.sort(key=lambda p: (p.name or "").lower())
        else:
            providers.sort(key=lambda p: p.model_count, reverse=True)
        if search:
            q = search.strip().lower()
            if q:
                providers = [
                    p
                    for p in providers
                    if q in (p.name or "").lower()
                    or q in (p.slug or "").lower()
                ]
        total = len(providers)
        page = providers[offset : offset + limit]
        return OpenRouterProviderListResponse(providers=page, total=total)

    async def get_openrouter_models_by_provider(
        self, provider_slug: str
    ) -> OpenRouterModelListResponse:
        """Get OpenRouter models hosted by a specific provider."""
        hosted_models_by_provider_slug = (
            await self._get_openrouter_hosted_models_by_provider_slug()
        )
        models = [
            OpenRouterModelBase.model_validate(model_dict)
            for model_dict in hosted_models_by_provider_slug.get(provider_slug, [])
        ]
        return OpenRouterModelListResponse(models=models, total=len(models))

    @cache_response(
        key_generator=lambda self, model_id: f"openrouter:model-providers:{model_id}",
        ttl=OPENROUTER_ENDPOINTS_CACHE_TTL_SECONDS,
        revive=OpenRouterProvidersByModelResponse,
    )
    async def get_openrouter_providers_by_model(
        self, model_id: str
    ) -> OpenRouterProvidersByModelResponse:
        """Get provider names for an OpenRouter model."""
        parts = model_id.split("/", 1)
        if len(parts) != 2:
            return OpenRouterProvidersByModelResponse(model_id=model_id, providers=[])

        author, slug = parts
        path = f"/models/{quote(author, safe='')}/{quote(slug, safe='')}/endpoints"
        try:
            json = await self._fetch_openrouter_json(path)
        except Exception as e:
            logger.warning(
                f"Failed to fetch OpenRouter model endpoints for '{model_id}': {e}"
            )
            return OpenRouterProvidersByModelResponse(model_id=model_id, providers=[])

        parsed = OpenRouterModelEndpointsApiResponse.model_validate(json)
        providers = [
            endpoint.provider_name
            for endpoint in parsed.data.endpoints
            if endpoint.provider_name
        ]
        return OpenRouterProvidersByModelResponse(model_id=model_id, providers=providers)

    async def _fetch_openrouter_json(self, path: str) -> dict:
        """Fetch JSON from OpenRouter API."""
        url = f"{OPENROUTER_API_BASE}{path}"
        async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

