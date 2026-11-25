# ORM: SQLAlchemy 2.x with separate Pydantic schemas (not SQLModel)

Status: accepted

The backend uses SQLAlchemy 2.x for persistence and separate Pydantic models for request/response
validation, instead of SQLModel. SQLModel was initially noted in the original PRD (§14.6), but
after analyzing the requirements — multi-table allocations, explicit transaction control with
row locks, and PostgreSQL-specific constraints (EXCLUDE) — SQLAlchemy 2.x plus Pydantic gives more
explicit control over complex relationships, transactions, and constraints.

Considered options: SQLModel (rejected: blends ORM and DTO concerns, making the exclusion
constraint and lock-heavy transaction code harder to express explicitly).

Consequences: two model layers (ORM models + Pydantic schemas) must be kept in sync by hand;
Alembic migrations are unaffected.
