"""Reservations and their per-table allocations (ER 2.0: RESERVATIONS,
RESERVATION_TABLE_ALLOCATIONS).

The EXCLUDE constraint is the hard database-level guarantee that no table has
overlapping active protected intervals (AC-02); it requires the btree_gist
extension.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

RESERVATION_STATUSES = ("active", "cancelled")
RESERVATION_SOURCES = ("online", "phone", "walk_in")


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("party_size > 0", name="ck_reservation_party_size_positive"),
        CheckConstraint("ends_at > starts_at", name="ck_reservation_ends_after_starts"),
        CheckConstraint(
            f"status IN ({', '.join(repr(s) for s in RESERVATION_STATUSES)})",
            name="ck_reservation_status",
        ),
        CheckConstraint(
            f"source IN ({', '.join(repr(s) for s in RESERVATION_SOURCES)})",
            name="ck_reservation_source",
        ),
        # online ⇒ no staff creator AND a manage token; anonymized rows are
        # exempt so the retention job can clear the token (ADR-0009)
        CheckConstraint(
            "source <> 'online' OR anonymized_at IS NOT NULL "
            "OR (created_by_staff_id IS NULL AND manage_token IS NOT NULL)",
            name="ck_online_reservation_token",
        ),
        # staff-created ⇒ staff creator set AND no manage token
        CheckConstraint(
            "source = 'online' OR (created_by_staff_id IS NOT NULL AND manage_token IS NULL)",
            name="ck_staff_reservation_creator",
        ),
        UniqueConstraint("manage_token", name="uq_reservation_manage_token"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    created_by_staff_id: Mapped[int | None] = mapped_column(
        ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    manage_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    anonymized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReservationTableAllocation(Base):
    """One row per (reservation, table). protected_from = starts_at,
    protected_until = ends_at + buffer. The EXCLUDE constraint makes overlapping
    active protected intervals on one table impossible (ADR-0002)."""

    __tablename__ = "reservation_table_allocations"
    __table_args__ = (
        PrimaryKeyConstraint("reservation_id", "table_id", name="pk_allocation"),
        ExcludeConstraint(
            ("table_id", "="),
            (func.tstzrange(text("protected_from"), text("protected_until")), "&&"),
            where=text("is_active"),
            name="no_overlapping_active_protected_intervals",
        ),
    )

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False
    )
    table_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant_tables.id", ondelete="CASCADE"), nullable=False
    )
    protected_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    protected_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
