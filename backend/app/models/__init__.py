"""All ORM models. Importing this package registers every table on Base.metadata."""

from .base import Base
from .customer import Customer
from .reservation import Reservation, ReservationTableAllocation
from .restaurant import BookingRules, OpeningHours, Restaurant
from .staff import StaffUser
from .tables import RestaurantTable, TableEnclave, TableNote

__all__ = [
    "Base",
    "BookingRules",
    "Customer",
    "OpeningHours",
    "Reservation",
    "ReservationTableAllocation",
    "Restaurant",
    "RestaurantTable",
    "StaffUser",
    "TableEnclave",
    "TableNote",
]
