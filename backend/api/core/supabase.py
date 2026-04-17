"""Supabase client configuration."""

import httpx
from supabase import Client, ClientOptions, create_client
from supabase_auth import SyncMemoryStorage

from api.core.config import settings

# Create Supabase client with secret key for server-side operations
# The secret key (formerly service_role) bypasses Row Level Security
# Longer timeout for auth (e.g. sign_in_with_password) to avoid ReadTimeout
_options = ClientOptions(
    storage=SyncMemoryStorage(),
    httpx_client=httpx.Client(timeout=30.0),
)
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SECRET_KEY,
    options=_options,
)


def get_supabase_client() -> Client:
    """Get the Supabase client instance."""
    return supabase
