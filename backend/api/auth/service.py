"""Authentication service using Supabase Auth."""

from api.auth.schemas import AuthResponse, LoginData, RefreshTokenRequest, UserCreate
from api.core.exceptions import BadRequestException, UnauthorizedException
from api.core.logging import get_logger
from api.core.supabase import get_supabase_client

logger = get_logger(__name__)


# Import AuthApiError - location varies by supabase-py version
try:
    from gotrue.errors import AuthApiError
except ImportError:
    try:
        from supabase.lib.client_options import AuthApiError
    except ImportError:
        # Fallback: create a generic exception class
        class AuthApiError(Exception):
            """Supabase Auth API Error."""

            def __init__(self, message: str = "Auth error"):
                self.message = message
                super().__init__(self.message)


class AuthService:
    """Service for handling authentication with Supabase."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def register(self, user_data: UserCreate) -> AuthResponse:
        """Register a new user with Supabase Auth.

        Args:
            user_data: User registration data (email, password)

        Returns:
            AuthResponse: Authentication tokens and user info

        Raises:
            BadRequestException: If registration fails
        """
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                }
            )

            if response.user is None:
                raise BadRequestException("Registration failed")

            # Check if email confirmation is required
            if response.session is None:
                # Email confirmation is enabled - user needs to verify email
                logger.info(
                    f"User registered, email confirmation required: {user_data.email}"
                )
                raise BadRequestException(
                    "Registration successful! Please check your email to confirm your account."
                )

            logger.info(f"User registered: {user_data.email}")
            return AuthResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
                user_id=response.user.id,
                email=response.user.email or "",
            )

        except AuthApiError as e:
            logger.error(f"Registration failed: {e.message}")
            raise BadRequestException(e.message)

    async def login(self, login_data: LoginData) -> AuthResponse:
        """Authenticate user with Supabase Auth.

        Args:
            login_data: Login credentials (email, password)

        Returns:
            AuthResponse: Authentication tokens and user info

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        try:
            response = self.supabase.auth.sign_in_with_password(
                {
                    "email": login_data.email,
                    "password": login_data.password,
                }
            )

            if response.user is None or response.session is None:
                raise UnauthorizedException("Invalid credentials")

            logger.info(f"User authenticated: {login_data.email}")
            return AuthResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
                user_id=response.user.id,
                email=response.user.email or "",
            )

        except AuthApiError as e:
            logger.error(f"Login failed: {e.message}")
            raise UnauthorizedException("Invalid email or password")

    async def refresh_token(self, refresh_data: RefreshTokenRequest) -> AuthResponse:
        """Refresh access token using refresh token.

        Args:
            refresh_data: Refresh token request

        Returns:
            AuthResponse: New authentication tokens

        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_data.refresh_token)

            if response.user is None or response.session is None:
                raise UnauthorizedException("Invalid refresh token")

            logger.info(f"Token refreshed for user: {response.user.email}")
            return AuthResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
                user_id=response.user.id,
                email=response.user.email or "",
            )

        except AuthApiError as e:
            logger.error(f"Token refresh failed: {e.message}")
            raise UnauthorizedException("Invalid or expired refresh token")

    async def logout(self, access_token: str) -> None:
        """Sign out user (invalidate session).

        Note: This requires the user's access token to be set in the client.
        For server-side logout, we typically just let tokens expire.
        """
        try:
            # Sign out the current session
            self.supabase.auth.sign_out()
            logger.info("User signed out")
        except AuthApiError as e:
            logger.error(f"Logout failed: {e.message}")
            # Don't raise - logout should be idempotent
