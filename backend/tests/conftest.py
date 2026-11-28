"""Shared pytest fixtures.

Environment variables are set before any app module is imported so that
settings load from the environment, exactly as in production (where values
come from the process environment / Render dashboard, never from git).

Database-backed tests use the DATABASE_URL test database (a postgres:16
service in CI; any local PostgreSQL 16 works).
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from app.config.settings import get_settings  # noqa: E402
from app.models import Base  # noqa: E402


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        conn.commit()
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """A session against a freshly created schema, dropped after each test."""
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    session = Session(bind=db_engine, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(db_engine)
