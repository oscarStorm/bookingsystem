"""Restaurant configuration: the restaurant itself, its booking rules, and
its per-weekday opening hours (ER 2.0: RESTAURANTS, BOOKING_RULES, OPENING_HOURS).
"""

from datetime import datetime, time

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)  # IANA, e.g. Europe/Copenhagen
    booking_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class BookingRules(Base):
    """One row per restaurant (UNIQUE restaurant_id). All values are read
    dynamically by the reservation logic — nothing is hardcoded there."""

    __tablename__ = "booking_rules"
    __table_args__ = (UniqueConstraint("restaurant_id", name="uq_booking_rules_restaurant"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    slot_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    reservation_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    buffer_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    max_online_party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    first_seating_start: Mapped[time] = mapped_column(Time, nullable=False)
    first_seating_last_start: Mapped[time] = mapped_column(Time, nullable=False)
    max_seatings_per_table: Mapped[int] = mapped_column(Integer, nullable=False)


class OpeningHours(Base):
    """Per-weekday hours in restaurant-local time. A weekday with no row is
    closed. close_time <= open_time means closing is on the following day
    (00:00 = next midnight)."""

    __tablename__ = "opening_hours"
    # day_of_week: 0 = Monday … 6 = Sunday (Python date.weekday())
    __table_args__ = (
        UniqueConstraint("restaurant_id", "day_of_week", name="uq_opening_hours_restaurant_day"),
        CheckConstraint(
            "open_time < kitchen_close_time", name="ck_opening_hours_open_before_kitchen_close"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    kitchen_close_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
