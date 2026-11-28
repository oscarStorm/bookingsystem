"""Seed seam: the demo seed script is idempotent — running it twice yields
exactly the Demo Restaurant dataset — and the admin password comes from the
caller (env var in production), never hardcoded; only an Argon2id hash is stored.
"""

from datetime import time

import pytest
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import func, select

from app.models import (
    BookingRules,
    OpeningHours,
    Restaurant,
    RestaurantTable,
    StaffUser,
    TableEnclave,
)
from scripts.seed import ADMIN_EMAIL, seed


def test_seed_twice_yields_exactly_the_demo_dataset(db_session):
    seed(db_session, admin_password="test-admin-password")
    seed(db_session, admin_password="test-admin-password")

    assert db_session.scalar(select(func.count(Restaurant.id))) == 1
    assert db_session.scalar(select(func.count(BookingRules.id))) == 1
    assert db_session.scalar(select(func.count(OpeningHours.id))) == 6  # Tue–Sun; Monday closed
    assert db_session.scalar(select(func.count(TableEnclave.id))) == 2
    assert db_session.scalar(select(func.count(RestaurantTable.id))) == 7
    assert db_session.scalar(select(func.count(StaffUser.id))) == 1


def test_seed_values_match_the_approved_dataset(db_session):
    seed(db_session, admin_password="test-admin-password")

    restaurant = db_session.get(Restaurant, 1)
    assert restaurant.name == "Demo Restaurant"
    assert restaurant.timezone == "Europe/Copenhagen"
    assert restaurant.booking_horizon_days == 30

    rules = db_session.scalar(select(BookingRules))
    assert rules.restaurant_id == 1
    assert rules.first_seating_start == time(17, 30)
    assert rules.first_seating_last_start == time(18, 15)
    assert rules.reservation_duration_minutes == 120
    assert rules.buffer_minutes == 15
    assert rules.slot_interval_minutes == 15
    assert rules.max_online_party_size == 6
    assert rules.max_seatings_per_table == 2

    hours = db_session.scalars(select(OpeningHours).order_by(OpeningHours.day_of_week)).all()
    assert [h.day_of_week for h in hours] == [1, 2, 3, 4, 5, 6]  # Tuesday–Sunday, Monday closed
    for h in hours:
        assert (h.open_time, h.kitchen_close_time, h.close_time) == (
            time(17, 30),
            time(21, 0),
            time(0, 0),
        )

    tables = {
        t.table_number: (t.capacity, t.enclave_id, t.allocation_priority)
        for t in db_session.scalars(select(RestaurantTable))
    }
    assert tables == {
        1: (4, None, 40),
        2: (2, None, 10),
        3: (2, 1, 30),
        4: (2, 1, 31),
        5: (2, 1, 32),
        6: (2, 2, 20),
        7: (2, 2, 21),
    }

    enclaves = {e.id: e.name for e in db_session.scalars(select(TableEnclave))}
    assert enclaves == {1: "Enclave 1", 2: "Enclave 2"}


def test_seed_staff_password_is_argon2id_hash_of_env_password(db_session):
    seed(db_session, admin_password="test-admin-password")

    staff = db_session.scalar(select(StaffUser).where(StaffUser.email == ADMIN_EMAIL))
    assert staff is not None
    assert staff.role == "admin"
    assert staff.password_hash != "test-admin-password"
    assert staff.password_hash.startswith("$argon2id$")
    # the stored hash verifies against the env-supplied password
    PasswordHasher().verify(staff.password_hash, "test-admin-password")
    with pytest.raises(VerifyMismatchError):
        PasswordHasher().verify(staff.password_hash, "wrong-password")


def test_seed_without_password_fails_instead_of_hardcoding_one(db_session):
    with pytest.raises(ValueError, match="SEED_ADMIN_PASSWORD"):
        seed(db_session, admin_password=None)
