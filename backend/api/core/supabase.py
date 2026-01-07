"""Supabase client configuration."""

from supabase import Client, create_client

from api.core.config import settings

# Create Supabase client with secret key for server-side operations
# The secret key (formerly service_role) bypasses Row Level Security
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SECRET_KEY,
)


def get_supabase_client() -> Client:
    """Get the Supabase client instance."""
    return supabase
