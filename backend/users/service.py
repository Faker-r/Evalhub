from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import NotFoundException
from backend.core.logging import get_logger
from backend.core.s3 import S3Storage
from backend.users.models import User
from backend.users.repository import UserRepository
from backend.users.schemas import ApiKeyCreate

logger = get_logger(__name__)


class UserService:
    """Service for handling user business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)
        self.s3 = S3Storage()

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        return await self.repository.get_by_id(user_id)

    # ==================== API Key Methods ====================

    def create_api_key(self, user_id: int, api_key_data: ApiKeyCreate) -> None:
        """Store an API key for a user.

        Args:
            user_id: User ID
            api_key_data: API key creation data
        """
        self.s3.upload_api_key(user_id, api_key_data.provider, api_key_data.api_key)
        logger.info(f"Stored API key for user {user_id}, provider {api_key_data.provider}")

    def get_api_key(self, user_id: int, provider: str) -> str:
        """Get an API key for a user (internal use only).

        Args:
            user_id: User ID
            provider: Provider name

        Returns:
            str: The API key

        Raises:
            NotFoundException: If the API key doesn't exist
        """
        try:
            return self.s3.download_api_key(user_id, provider)
        except FileNotFoundError:
            raise NotFoundException(f"API key not found for provider: {provider}")

    def list_api_keys(self, user_id: int) -> list[str]:
        """List all API key providers for a user.

        Args:
            user_id: User ID

        Returns:
            list[str]: List of provider names
        """
        return self.s3.list_user_api_keys(user_id)

    def delete_api_key(self, user_id: int, provider: str) -> None:
        """Delete an API key for a user.

        Args:
            user_id: User ID
            provider: Provider name

        Raises:
            NotFoundException: If the API key doesn't exist
        """
        if not self.s3.api_key_exists(user_id, provider):
            raise NotFoundException(f"API key not found for provider: {provider}")

        self.s3.delete_api_key(user_id, provider)
        logger.info(f"Deleted API key for user {user_id}, provider {provider}")
