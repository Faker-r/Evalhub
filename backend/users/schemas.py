from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


# ==================== API Key Schemas ====================


class ApiKeyCreate(BaseModel):
    """API key creation schema."""

    provider: str
    api_key: str


class ApiKeyResponse(BaseModel):
    """API key response schema (without the actual key)."""

    provider: str


class ApiKeyListResponse(BaseModel):
    """Response schema for listing API keys."""

    api_key_providers: list[ApiKeyResponse]
