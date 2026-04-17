"""User schemas."""

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User response schema."""

    id: str  # Supabase UUID
    email: EmailStr


# ==================== API Key Schemas ====================


class ApiKeyCreate(BaseModel):
    """API key creation schema."""

    provider_id: str
    api_key: str


class ApiKeyResponse(BaseModel):
    """API key response schema (without the actual key)."""

    provider_id: str
    provider_name: str


class ApiKeyListResponse(BaseModel):
    """Response schema for listing API keys."""

    api_key_providers: list[ApiKeyResponse]
