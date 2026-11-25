"""Physical tables, enclaves, and staff table notes (ER 2.0: TABLE_ENCLAVES,
RESTAURANT_TABLES, TABLE_NOTES)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TableEnclave(Base):
    """A named group of tables that may be physically joined. Tables with
    enclave_id NULL cannot be joined; different enclaves cannot be mixed."""

    __tablename__ = "table_enclaves"
    __table_args__ = (UniqueConstraint("restaurant_id", "name", name="uq_enclave_restaurant_name"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "table_number", name="uq_table_restaurant_number"),
        CheckConstraint("capacity > 0", name="ck_table_capacity_positive"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    enclave_id: Mapped[int | None] = mapped_column(
        ForeignKey("table_enclaves.id", ondelete="SET NULL"), nullable=True
    )
    table_number: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    # Tie-breaker only: lower is preferred.
    allocation_priority: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)


class TableNote(Base):
    """Staff-only note on a table with optional expiry. Never blocks capacity."""

    __tablename__ = "table_notes"
    __table_args__ = (
        CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_table_note_expiry_after_created",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant_tables.id", ondelete="CASCADE"), nullable=False
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff_users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
