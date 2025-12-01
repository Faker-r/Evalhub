from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    """Login data schema."""

    email: EmailStr
    password: str

