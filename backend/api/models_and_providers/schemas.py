"""Models and providers schemas."""

from pydantic import BaseModel, HttpUrl


# ==================== Provider Schemas ====================


class ProviderBase(BaseModel):
    """Base provider schema."""

    name: str
    slug: str | None = None
    base_url: str


class ProviderCreate(ProviderBase):
    """Provider creation schema."""

    pass


class ProviderUpdate(BaseModel):
    """Provider update schema."""

    name: str | None = None
    base_url: str | None = None


class ProviderResponse(ProviderBase):
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


class ModelBase(BaseModel):
    """Base model schema."""

    display_name: str
    developer: str
    api_name: str
    slug: str | None = None


class ModelCreate(ModelBase):
    """Model creation schema."""

    provider_ids: list[int]


class ModelUpdate(BaseModel):
    """Model update schema."""

    display_name: str | None = None
    developer: str | None = None
    api_name: str | None = None
    provider_ids: list[int] | None = None


class ModelResponse(ModelBase):
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
