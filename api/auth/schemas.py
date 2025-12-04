"""Authentication schemas for Supabase Auth."""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str


class LoginData(BaseModel):
    """Login data schema."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str
