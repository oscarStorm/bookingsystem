"""Declarative base for all ORM models (ADR-0001: SQLAlchemy 2.x)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
