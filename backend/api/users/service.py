"""User service for non-auth operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import NotFoundException
from api.core.logging import get_logger
from api.core.s3 import S3Storage
from api.models_and_providers.models import Provider
from api.users.schemas import ApiKeyCreate, ApiKeyResponse

logger = get_logger(__name__)


class UserService:
    """Service for handling user business logic (API keys, etc.)."""

    def __init__(self, session: AsyncSession | None = None):
        self.s3 = S3Storage()
        self.session = session

    # ==================== API Key Methods ====================

    async def create_api_key(self, user_id: str, api_key_data: ApiKeyCreate) -> ApiKeyResponse:
        """Store an API key for a user.

        Args:
            user_id: User ID (Supabase UUID)
            api_key_data: API key creation data

        Returns:
            ApiKeyResponse: API key response with provider info

        Raises:
            NotFoundException: If provider not found
        """
        if not self.session:
            raise ValueError("Database session required for API key operations")

        # Verify provider exists and get its name
        stmt = select(Provider).where(Provider.id == api_key_data.provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {api_key_data.provider_id} not found")

        # Store API key using provider name
        self.s3.upload_api_key(user_id, provider.name, api_key_data.api_key)
        logger.info(f"Stored API key for user {user_id}, provider {provider.name}")

        return ApiKeyResponse(provider_id=provider.id, provider_name=provider.name)

    async def get_api_key(self, user_id: str, provider_id: int) -> str:
        """Get an API key for a user (internal use only).

        Args:
            user_id: User ID (Supabase UUID)
            provider_id: Provider ID

        Returns:
            str: The API key

        Raises:
            NotFoundException: If the provider or API key doesn't exist
        """
        if not self.session:
            raise ValueError("Database session required for API key operations")

        # Get provider name from ID
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {provider_id} not found")

        try:
            return self.s3.download_api_key(user_id, provider.name)
        except FileNotFoundError:
            raise NotFoundException(f"API key not found for provider: {provider.name}")

    async def list_api_keys(self, user_id: str) -> list[ApiKeyResponse]:
        """List all API key providers for a user.

        Args:
            user_id: User ID (Supabase UUID)

        Returns:
            list[ApiKeyResponse]: List of API key responses with provider info
        """
        if not self.session:
            raise ValueError("Database session required for API key operations")
        
        # Get provider names from S3
        provider_names = self.s3.list_user_api_keys(user_id)

        # Map provider names to provider IDs
        api_keys = []
        for provider_name in provider_names:
            stmt = select(Provider).where(Provider.name == provider_name)
            result = await self.session.execute(stmt)
            provider = result.scalar_one_or_none()

            if provider:
                api_keys.append(
                    ApiKeyResponse(provider_id=provider.id, provider_name=provider.name)
                )
            else:
                # Provider exists in S3 but not in database - log warning
                logger.warning(
                    f"API key for provider '{provider_name}' exists but provider not in database"
                )

        return api_keys

    async def delete_api_key(self, user_id: str, provider_id: int) -> None:
        """Delete an API key for a user.

        Args:
            user_id: User ID (Supabase UUID)
            provider_id: Provider ID

        Raises:
            NotFoundException: If the provider or API key doesn't exist
        """
        if not self.session:
            raise ValueError("Database session required for API key operations")

        # Get provider name from ID
        stmt = select(Provider).where(Provider.id == provider_id)
        result = await self.session.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise NotFoundException(f"Provider with ID {provider_id} not found")

        if not self.s3.api_key_exists(user_id, provider.name):
            raise NotFoundException(f"API key not found for provider: {provider.name}")

        self.s3.delete_api_key(user_id, provider.name)
        logger.info(f"Deleted API key for user {user_id}, provider {provider.name}")
