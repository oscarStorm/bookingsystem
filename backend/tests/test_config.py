"""Config seam: settings are read from environment variables (locally via a
gitignored .env file). Secrets must never be hardcoded — a missing required
value fails fast instead of falling back to a default.
"""

import pytest
from pydantic import ValidationError

from app.config import settings as settings_module


@pytest.fixture(autouse=True)
def clear_settings_cache(monkeypatch):
    # Isolate tests from any real local .env file: only process env vars count.
    monkeypatch.setitem(settings_module.Settings.model_config, "env_file", ())
    settings_module.get_settings.cache_clear()
    yield
    settings_module.get_settings.cache_clear()


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://db.example:5432/restaurant")
    monkeypatch.setenv("SECRET_KEY", "s3cret")
    monkeypatch.setenv("RESEND_API_KEY", "re_123456")
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "admin-pw")

    settings = settings_module.get_settings()

    assert settings.database_url == "postgresql+psycopg://db.example:5432/restaurant"
    assert settings.secret_key == "s3cret"
    assert settings.resend_api_key == "re_123456"
    assert settings.seed_admin_password == "admin-pw"


@pytest.mark.parametrize("missing_var", ["DATABASE_URL", "SECRET_KEY"])
def test_missing_required_secret_fails_fast(monkeypatch, missing_var):
    monkeypatch.delenv(missing_var, raising=False)

    with pytest.raises(ValidationError):
        settings_module.Settings()


def test_optional_email_and_seed_password_default_to_none(monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("SEED_ADMIN_PASSWORD", raising=False)

    settings = settings_module.get_settings()

    assert settings.resend_api_key is None
    assert settings.seed_admin_password is None
