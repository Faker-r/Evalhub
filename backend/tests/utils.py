import uuid
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session.

    Yields:
        AsyncSession: Test database session
    """
    async for session in get_session():
        yield session


def get_test_user_id() -> str:
    """Get a test user ID.

    Returns:
        str: Test user ID (UUID)
    """
    return "e01da140-64b2-4ab9-b379-4f55dcaf0b22"
