"""Security utilities for Supabase JWT verification."""

import base64
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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


def _get_jwt_secret() -> bytes:
    """Decode the Supabase JWT secret from base64."""
    return base64.b64decode(settings.SUPABASE_JWT_SECRET)


def _decode_token(token: str) -> dict:
    """Verify and decode a Supabase JWT using the local JWT secret (HS256).

    Supabase signs JWTs with the project's JWT secret, so we can verify
    locally without a network round-trip to the JWKS endpoint.
    """
    return jwt.decode(
        token,
        _get_jwt_secret(),
        algorithms=["HS256"],
        options={"verify_aud": False},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Dependency to get current authenticated user from Supabase JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = _decode_token(token)

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


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> CurrentUser | None:
    """Dependency to optionally get current authenticated user.

    Returns None if no credentials provided, otherwise validates like get_current_user.
    """
    if credentials is None:
        return None

    try:
        payload = _decode_token(credentials.credentials)

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None:
            return None

        logger.debug(f"Authenticated user: {email} ({user_id})")
        return CurrentUser(id=user_id, email=email or "")

    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
        return None
