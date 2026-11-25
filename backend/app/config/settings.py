"""Environment-based configuration.

All values come from the process environment; locally they are provided by a
gitignored `.env` file (see `.env.example` at the repo root). Secrets
(DATABASE_URL, SECRET_KEY, RESEND_API_KEY, SEED_ADMIN_PASSWORD) must never be
hardcoded or committed — required values fail fast when missing.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # `.env` next to the backend working directory, or one level up at the
        # repo root — both are gitignored.
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"

    # PostgreSQL connection string (Neon Frankfurt in prod, sslmode=require)
    database_url: str

    # Secret used to sign the staff session cookie
    secret_key: str

    # Resend API key for the single confirmation email (optional in dev)
    resend_api_key: str | None = None

    # Password for the seeded admin staff account (consumed by the seed script)
    seed_admin_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
