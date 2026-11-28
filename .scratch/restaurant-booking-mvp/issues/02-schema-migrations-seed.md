# 02: Schema, migrations, and demo seed

**What to build:** SQLAlchemy 2.x models for all ten tables (restaurants, booking_rules, opening_hours, table_enclaves, restaurant_tables, staff_users, customers, reservations, reservation_table_allocations, table_notes) with every integrity rule from the ER 2.0 design: UNIQUE constraints, CHECKs (party_size > 0, capacity > 0, ends_at > starts_at, expires_at > created_at when present, status/source enums, online ⇒ manage_token set and no staff creator, staff-created ⇒ creator set and no token), and the EXCLUDE USING gist constraint (`table_id =`, `tstzrange(protected_from, protected_until) &&`) WHERE is_active on allocations, backed by the btree_gist extension. An Alembic migration creates it all on PostgreSQL 16. Separately, an idempotent seed script creates the Demo Restaurant dataset: restaurant Europe/Copenhagen with 30-day horizon, booking rules, opening hours Tue–Sun (Monday closed — no row), two enclaves, seven tables with allocation priorities, and one admin staff account whose Argon2id hash is computed from a password supplied via environment variable. Migrations carry schema only; seed data lives in the standalone script.

**Blocked by:** 01.

**Status:** done

- [x] `alembic upgrade head` on a fresh test database creates the full schema including the EXCLUDE constraint; downgrade works
- [x] Running the seed script twice yields exactly one restaurant, one booking-rules row, one opening-hours row per open weekday, two enclaves, seven tables, one staff account — no duplicates
- [x] Admin password comes from an env var; no secret appears in the script or in git
- [x] Constraint tests pass: the EXCLUDE constraint rejects overlapping active protected intervals on the same table

## Comments

Implemented in the commit "Add ER 2.0 schema, initial Alembic migration, and idempotent demo seed (ticket 02)": SQLAlchemy 2.x models for all ten tables, hand-written migration 0001 (btree_gist extension + EXCLUDE constraint), idempotent `scripts/seed.py` (Argon2id hash of SEED_ADMIN_PASSWORD, sequences advanced after fixed-id inserts). 30 tests green (constraints, migration up/down on a scratch DB, seed idempotency/values), mypy clean. Code review fixed: BigInteger PKs on all models to match ER 2.0, anonymization-safe online-token CHECK (ADR-0009), glossary wording.
