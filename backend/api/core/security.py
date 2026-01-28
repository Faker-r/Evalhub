"""Security utilities for Supabase JWT verification."""

from dataclasses import dataclass
from functools import lru_cache

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from api.core.config import settings
from api.core.logging import get_logger

logger = get_logger(__name__)

# Use HTTPBearer for Supabase JWT tokens
security = HTTPBearer()


@dataclass
class CurrentUser:
    """Represents the current authenticated user from Supabase."""

    id: str  # Supabase user UUID
    email: str


@lru_cache()
def get_jwks_client() -> PyJWKClient:
    """Get a cached JWKS client for Supabase.

    Supabase exposes public keys at: {SUPABASE_URL}/auth/v1/.well-known/jwks.json
    """
    jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Dependency to get current authenticated user from Supabase JWT.

    Verifies the JWT token using Supabase's public keys (JWKS).

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        CurrentUser: The authenticated user's info

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        # Get the signing key from Supabase JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify the JWT using the public key
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],  # Supabase uses RS256 or ES256
            options={"verify_aud": False},
        )

        # Extract user info from the JWT payload
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None:
            logger.error("JWT payload missing 'sub' field")
            raise credentials_exception

        logger.debug(f"Authenticated user: {email} ({user_id})")
        return CurrentUser(id=user_id, email=email or "")

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during JWT validation: {e}")
        raise credentials_exception
