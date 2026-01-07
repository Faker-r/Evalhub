from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from api.core.config import settings

# Convert DATABASE_URL to async driver and remove sslmode parameter
database_url = settings.DATABASE_URL

# Configure SSL for asyncpg (Supabase requires SSL)
connect_args = {"ssl": "require"}

# Create async engine
engine = create_async_engine(
    database_url, echo=False, future=True, connect_args=connect_args
)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base for models
Base = declarative_base()


async def get_session() -> AsyncSession:
    """Dependency for getting async database session.

    Yields:
        AsyncSession: Async database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
