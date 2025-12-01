from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import LoginData, Token, UserCreate
from api.core.config import settings
from api.core.exceptions import UnauthorizedException
from api.core.logging import get_logger
from api.core.security import create_access_token, verify_password
from api.users.models import User
from api.users.repository import UserRepository

logger = get_logger(__name__)


class AuthService:
    """Service for handling authentication business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        return await self.repository.create(user_data)

    async def login(self, login_data: LoginData) -> Token:
        """Authenticate user and return token."""
        # Get user
        user = await self.repository.get_by_email(login_data.email)

        # Verify credentials
        if not user or not verify_password(
            login_data.password, str(user.hashed_password)
        ):
            raise UnauthorizedException(detail="Incorrect email or password")

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.JWT_EXPIRATION),
        )

        logger.info(f"User authenticated: {user.email}")
        return Token(access_token=access_token)

