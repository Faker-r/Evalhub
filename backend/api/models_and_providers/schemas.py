"""Models and providers schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict

# ==================== Provider Schemas ====================


class BaseProviderSchema(BaseModel):
    """Base provider schema shared by standard and OpenRouter providers."""

    name: str


class StandardProviderBase(BaseProviderSchema):
    """Base schema for standard providers."""

    slug: str | None = None
    base_url: str


class ProviderCreate(StandardProviderBase):
    """Provider creation schema."""

    pass


class ProviderUpdate(BaseModel):
    """Provider update schema."""

    name: str | None = None
    base_url: str | None = None


class ProviderResponse(StandardProviderBase):
    """Provider response schema."""

    id: int

    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """Response schema for listing providers."""

    providers: list[ProviderResponse]
    total: int
    page: int
    page_size: int


# ==================== Model Schemas ====================


class BaseModelSchema(BaseModel):
    """Base model schema shared by standard and OpenRouter models."""


class StandardModelBase(BaseModelSchema):
    """Base schema for standard models."""

    display_name: str
    developer: str
    api_name: str


class ModelCreate(StandardModelBase):
    """Model creation schema."""

    provider_ids: list[int]


class ModelUpdate(BaseModel):
    """Model update schema."""

    display_name: str | None = None
    developer: str | None = None
    api_name: str | None = None
    provider_ids: list[int] | None = None


class ModelResponse(StandardModelBase):
    """Model response schema."""

    id: int
    providers: list[ProviderResponse]

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    """Response schema for listing models."""

    models: list[ModelResponse]
    total: int
    page: int
    page_size: int


# ==================== OpenRouter Schemas ====================


class OpenRouterModelIcon(BaseModel):
    """OpenRouter model icon payload."""

    url: str | None = None


class OpenRouterModelBase(BaseModelSchema):
    """Base schema for OpenRouter models."""

    id: str
    name: str
    description: str | None = None
    pricing: dict[str, Any] | None = None
    context_length: int | None = None
    canonical_slug: str | None = None
    architecture: dict[str, Any] | None = None
    top_provider: dict[str, Any] | None = None
    supported_parameters: list[str] | None = None
    per_request_limits: dict[str, Any] | None = None
    provider_slugs: list[str] | None = None
    icon: OpenRouterModelIcon | None = None


class OpenRouterModelListResponse(BaseModel):
    """Response schema for listing OpenRouter models."""

    models: list[OpenRouterModelBase]
    total: int


class OpenRouterProviderBase(BaseProviderSchema):
    """Base schema for OpenRouter providers."""

    slug: str


class OpenRouterProviderResponse(OpenRouterProviderBase):
    """OpenRouter provider response schema."""

    model_count: int
    privacy_policy_url: str | None = None
    terms_of_service_url: str | None = None
    status_page_url: str | None = None


class OpenRouterProviderListResponse(BaseModel):
    """Response schema for listing OpenRouter providers."""

    providers: list[OpenRouterProviderResponse]
    total: int


class OpenRouterProvidersByModelResponse(BaseModel):
    """Response schema for listing providers for one OpenRouter model."""

    model_id: str
    providers: list[str]


class OpenRouterModelsApiResponse(BaseModel):
    """OpenRouter upstream /models response schema."""

    data: list[OpenRouterModelBase]


class OpenRouterProviderApiModel(OpenRouterProviderBase):
    """OpenRouter upstream provider payload model."""

    model_config = ConfigDict(extra="allow")

    website_url: str | None = None
    homepage_url: str | None = None
    url: str | None = None
    privacy_policy_url: str | None = None
    terms_of_service_url: str | None = None
    status_page_url: str | None = None


class OpenRouterProvidersApiResponse(BaseModel):
    """OpenRouter upstream /providers response schema."""

    data: list[OpenRouterProviderApiModel]


class OpenRouterModelEndpoint(BaseModel):
    """OpenRouter upstream model endpoint payload."""

    provider_name: str | None = None


class OpenRouterModelEndpointsData(BaseModel):
    """OpenRouter upstream model endpoints wrapper."""

    endpoints: list[OpenRouterModelEndpoint]


class OpenRouterModelEndpointsApiResponse(BaseModel):
    """OpenRouter upstream /models/{id}/endpoints response schema."""

    data: OpenRouterModelEndpointsData
