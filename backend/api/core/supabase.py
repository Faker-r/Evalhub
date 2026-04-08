"""Supabase client configuration."""

import httpx

from supabase import Client, ClientOptions, create_client
from supabase_auth import SyncMemoryStorage

from api.core.config import settings

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get the Supabase client instance (lazy-initialized)."""
    global _supabase_client
    if _supabase_client is None:
        options = ClientOptions(
            storage=SyncMemoryStorage(),
            httpx_client=httpx.Client(timeout=30.0),
        )
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET_KEY,
            options=options,
        )
    return _supabase_client
