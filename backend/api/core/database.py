from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from api.core.config import settings

# Convert DATABASE_URL to async driver and remove sslmode parameter
database_url = settings.DATABASE_URL

_db_url_lower = settings.DATABASE_URL.lower()
# Remote DBs (e.g. Supabase) need TLS; typical local Postgres in CI/tests does not.
_use_asyncpg_ssl = not any(h in _db_url_lower for h in ("localhost", "127.0.0.1"))

# Configure SSL for asyncpg when required.
# Disable prepared statement cache for pgbouncer compatibility
connect_args = {"statement_cache_size": 0}
if _use_asyncpg_ssl:
    connect_args["ssl"] = "require"

# Create async engine
engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
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
            try:
                await session.close()
            except sqlalchemy_exc.InterfaceError:
                pass
