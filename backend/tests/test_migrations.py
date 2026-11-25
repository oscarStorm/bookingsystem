"""Migration seam: `alembic upgrade head` on a fresh database creates the full
schema (all ten tables + the EXCLUDE constraint backed by btree_gist), and
`downgrade base` removes it again. Runs against a scratch database derived
from DATABASE_URL so the test database itself is untouched.
"""

import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, make_url, text

from app.config.settings import get_settings

BACKEND_DIR = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = {
    "restaurants",
    "booking_rules",
    "opening_hours",
    "table_enclaves",
    "restaurant_tables",
    "staff_users",
    "customers",
    "reservations",
    "reservation_table_allocations",
    "table_notes",
}


def alembic_config(url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def public_tables(url: str) -> set[str]:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            return {row[0] for row in rows}
    finally:
        engine.dispose()


def exclude_constraints(url: str) -> list[str]:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT conname FROM pg_constraint WHERE contype = 'x'"))
            return [row[0] for row in rows]
    finally:
        engine.dispose()


def test_upgrade_head_creates_full_schema_and_downgrade_removes_it():
    base = make_url(get_settings().database_url)
    maintenance_url = str(base.set(database="postgres"))
    scratch = f"alembic_test_{uuid.uuid4().hex[:12]}"
    scratch_url = str(base.set(database=scratch))

    admin = create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{scratch}"'))
        conn.execute(text(f'CREATE DATABASE "{scratch}"'))
    admin.dispose()

    try:
        command.upgrade(alembic_config(scratch_url), "head")
        assert EXPECTED_TABLES <= public_tables(scratch_url)
        assert any(
            "no_overlap" in name for name in exclude_constraints(scratch_url)
        ), "EXCLUDE constraint on active protected intervals must exist"

        command.downgrade(alembic_config(scratch_url), "base")
        assert EXPECTED_TABLES.isdisjoint(public_tables(scratch_url))
    finally:
        admin = create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{scratch}"'))
        admin.dispose()
