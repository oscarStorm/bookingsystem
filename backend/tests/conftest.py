"""Shared pytest fixtures.

Environment variables are set before any app module is imported so that
settings load from the environment, exactly as in production (where values
come from the process environment / Render dashboard, never from git).
"""

import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
