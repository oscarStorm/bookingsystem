"""Schema seam: PostgreSQL itself enforces the ER 2.0 integrity rules —
the EXCLUDE constraint on active protected intervals, CHECKs, and UNIQUEs.
Tests insert through the ORM and assert the database rejects violations.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Reservation,
    ReservationTableAllocation,
    Restaurant,
    RestaurantTable,
    StaffUser,
    TableNote,
)

UTC = timezone.utc
START = datetime(2025, 6, 10, 17, 30, tzinfo=UTC)  # a Tuesday evening
END = START + timedelta(hours=2)


def make_restaurant(db_session) -> Restaurant:
    restaurant = Restaurant(
        id=1, name="Demo Restaurant", timezone="Europe/Copenhagen", booking_horizon_days=30
    )
    db_session.add(restaurant)
    db_session.commit()
    return restaurant


def make_table(db_session, restaurant, number=1) -> RestaurantTable:
    table = RestaurantTable(
        restaurant_id=restaurant.id,
        table_number=number,
        capacity=4,
        enclave_id=None,
        allocation_priority=10,
        is_active=True,
    )
    db_session.add(table)
    db_session.commit()
    return table


def make_reservation(db_session, restaurant, **overrides) -> Reservation:
    defaults = dict(
        restaurant_id=restaurant.id,
        starts_at=START,
        ends_at=END,
        party_size=2,
        status="active",
        source="online",
        is_locked=False,
        manage_token=uuid.uuid4(),
    )
    defaults.update(overrides)
    reservation = Reservation(**defaults)
    db_session.add(reservation)
    db_session.commit()
    return reservation


def add_allocation(db_session, reservation, table, active=True, until=None) -> None:
    db_session.add(
        ReservationTableAllocation(
            reservation_id=reservation.id,
            table_id=table.id,
            protected_from=reservation.starts_at,
            protected_until=until or (reservation.ends_at + timedelta(minutes=15)),
            is_active=active,
        )
    )
    db_session.commit()


def test_exclude_constraint_rejects_overlapping_active_protected_intervals(
    db_session,
):
    restaurant = make_restaurant(db_session)
    table = make_table(db_session, restaurant)
    first = make_reservation(db_session, restaurant)
    add_allocation(db_session, first, table)

    overlapping = make_reservation(
        db_session, restaurant, starts_at=START + timedelta(minutes=30)
    )
    with pytest.raises(IntegrityError):
        add_allocation(db_session, overlapping, table)
    db_session.rollback()


def test_exclude_constraint_allows_back_to_back_outside_buffer(db_session):
    restaurant = make_restaurant(db_session)
    table = make_table(db_session, restaurant)
    first = make_reservation(db_session, restaurant)
    add_allocation(db_session, first, table)  # protected until END + 15 min

    # starts exactly when the protected interval of the first ends: allowed
    second = make_reservation(
        db_session, restaurant, starts_at=END + timedelta(minutes=15), ends_at=END + timedelta(hours=2)
    )
    add_allocation(db_session, second, table)
    assert db_session.query(ReservationTableAllocation).count() == 2


def test_exclude_constraint_ignores_inactive_allocations(db_session):
    restaurant = make_restaurant(db_session)
    table = make_table(db_session, restaurant)
    cancelled = make_reservation(db_session, restaurant, status="cancelled")
    add_allocation(db_session, cancelled, table, active=False)

    other = make_reservation(db_session, restaurant)
    add_allocation(db_session, other, table, active=True)  # same interval, must be allowed
    assert db_session.query(ReservationTableAllocation).count() == 2


def test_check_party_size_positive(db_session):
    restaurant = make_restaurant(db_session)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, party_size=0)
    db_session.rollback()


def test_check_ends_after_starts(db_session):
    restaurant = make_restaurant(db_session)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, ends_at=START)
    db_session.rollback()


@pytest.mark.parametrize("bad_status", ["pending", "done"])
def test_check_status_enum(db_session, bad_status):
    restaurant = make_restaurant(db_session)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, status=bad_status)
    db_session.rollback()


@pytest.mark.parametrize("bad_source", ["email", "carrier_pigeon"])
def test_check_source_enum(db_session, bad_source):
    restaurant = make_restaurant(db_session)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, source=bad_source)
    db_session.rollback()


def test_check_online_reservation_requires_manage_token(db_session):
    restaurant = make_restaurant(db_session)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, source="online", manage_token=None)
    db_session.rollback()


def test_check_online_reservation_has_no_staff_creator(db_session):
    restaurant = make_restaurant(db_session)
    staff = StaffUser(
        restaurant_id=restaurant.id,
        name="Admin",
        email="admin@example.com",
        password_hash="x",
        role="admin",
    )
    db_session.add(staff)
    db_session.commit()
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, source="online", created_by_staff_id=staff.id)
    db_session.rollback()


def test_check_staff_reservation_has_creator_and_no_token(db_session):
    restaurant = make_restaurant(db_session)
    staff = StaffUser(
        restaurant_id=restaurant.id,
        name="Admin",
        email="admin@example.com",
        password_hash="x",
        role="admin",
    )
    db_session.add(staff)
    db_session.commit()
    # staff-created but with a manage token: rejected
    with pytest.raises(IntegrityError):
        make_reservation(
            db_session, restaurant, source="walk_in", created_by_staff_id=staff.id
        )
    db_session.rollback()
    # staff-created without token: allowed (anonymous walk-in)
    walk_in = make_reservation(
        db_session, restaurant, source="walk_in", manage_token=None, created_by_staff_id=staff.id
    )
    assert walk_in.customer_id is None


def test_unique_staff_email(db_session):
    restaurant = make_restaurant(db_session)
    db_session.add(
        StaffUser(
            restaurant_id=restaurant.id,
            name="A",
            email="admin@example.com",
            password_hash="x",
            role="admin",
        )
    )
    db_session.commit()
    with pytest.raises(IntegrityError):
        db_session.add(
            StaffUser(
                restaurant_id=restaurant.id,
                name="B",
                email="admin@example.com",
                password_hash="y",
                role="admin",
            )
        )
        db_session.commit()
    db_session.rollback()


def test_unique_table_number_per_restaurant(db_session):
    restaurant = make_restaurant(db_session)
    make_table(db_session, restaurant, number=1)
    with pytest.raises(IntegrityError):
        make_table(db_session, restaurant, number=1)
    db_session.rollback()


def test_unique_manage_token(db_session):
    restaurant = make_restaurant(db_session)
    token = uuid.uuid4()
    make_reservation(db_session, restaurant, manage_token=token)
    with pytest.raises(IntegrityError):
        make_reservation(db_session, restaurant, manage_token=token)
    db_session.rollback()


def test_anonymized_online_reservation_may_clear_token(db_session):
    """ADR-0009: the retention job nulls manage_token/customer on old online
    reservations; the CHECK constraints must permit that."""
    restaurant = make_restaurant(db_session)
    reservation = make_reservation(db_session, restaurant, source="online")
    reservation.manage_token = None
    reservation.customer_id = None
    reservation.anonymized_at = datetime.now(UTC)
    db_session.commit()  # must not raise
    assert reservation.anonymized_at is not None


def test_check_table_note_expiry_after_creation(db_session):
    restaurant = make_restaurant(db_session)
    table = make_table(db_session, restaurant)
    staff = StaffUser(
        restaurant_id=restaurant.id,
        name="Admin",
        email="admin@example.com",
        password_hash="x",
        role="admin",
    )
    db_session.add(staff)
    db_session.commit()
    with pytest.raises(IntegrityError):
        db_session.add(
            TableNote(
                table_id=table.id,
                staff_id=staff.id,
                content="broken chair",
                expires_at=datetime.now(UTC) - timedelta(days=1),
            )
        )
        db_session.commit()
    db_session.rollback()
