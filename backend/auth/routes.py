from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.schemas import LoginData, Token, UserCreate
from backend.auth.service import AuthService
from backend.core.database import get_session
from backend.core.logging import get_logger
from backend.users.schemas import UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Register a new user."""
    logger.debug(f"Registering user: {user_data.email}")
    return await AuthService(session).register(user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> Token:
    """Authenticate user and return token."""
    login_data = LoginData(email=form_data.username, password=form_data.password)
    logger.debug(f"Login attempt: {login_data.email}")
    return await AuthService(session).login(login_data)

