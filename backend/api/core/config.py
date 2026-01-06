from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "Evalhub"
    DATABASE_URL: str
    DEBUG: bool = False

    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str  # Replaces legacy "anon" key
    SUPABASE_SECRET_KEY: str  # Replaces legacy "service_role" key
    SUPABASE_JWT_SECRET: str

    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-2"
    S3_BUCKET_NAME: str = "evalhub-bucket"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
