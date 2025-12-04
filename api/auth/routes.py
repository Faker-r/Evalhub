"""Authentication routes using Supabase Auth."""

from fastapi import APIRouter, Depends, status

from api.auth.schemas import AuthResponse, LoginData, RefreshTokenRequest, UserCreate
from api.auth.service import AuthService
from api.core.logging import get_logger
from api.core.security import CurrentUser, get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> AuthResponse:
    """Register a new user.

    Creates a new user account in Supabase Auth.
    Returns access and refresh tokens upon successful registration.
    """
    logger.debug(f"Registering user: {user_data.email}")
    return await AuthService().register(user_data)


@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginData) -> AuthResponse:
    """Authenticate user and return tokens.

    Validates credentials against Supabase Auth and returns
    access and refresh tokens.
    """
    logger.debug(f"Login attempt: {login_data.email}")
    return await AuthService().login(login_data)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_data: RefreshTokenRequest) -> AuthResponse:
    """Refresh access token.

    Use the refresh token to obtain a new access token
    when the current one expires.
    """
    logger.debug("Token refresh requested")
    return await AuthService().refresh_token(refresh_data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: CurrentUser = Depends(get_current_user)) -> None:
    """Log out current user.

    Invalidates the current session. Note that the access token
    will remain valid until it expires.
    """
    logger.debug(f"Logout requested for user: {current_user.email}")
    await AuthService().logout("")
