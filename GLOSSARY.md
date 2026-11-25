# Restaurant Booking System

Domain vocabulary for the booking context. This is the single context for the MVP: customers
reserve tables online, staff administer reservations. Use these terms in issues, code, tests,
and docs — do not drift to the avoided synonyms.

## Booking and seating

**Reservation**:
A confirmed booking of one or more tables for a party at a start time. Immutable after creation
except for its table allocation.
_Avoid_: "booking" as a noun for the persisted record

**Seating**:
One of the two daily seating periods on a table. A table may have a first seating and a second
seating in the same evening.
_Avoid_: turn, sitting

**Seating window**:
The range of allowed start times for a seating. The first window is configured directly
(17:30–18:15); the second window is derived from the first plus duration and buffer (19:45–20:30).

**Slot**:
A bookable start time: a point on the slot-interval grid (15 minutes) inside a seating window.
_Avoid_: "time slot" when it could mean the whole window

**Duration**:
How long a reservation occupies its tables (120 minutes for online reservations; staff may override).

**Buffer**:
The mandatory gap (15 minutes) after a reservation's end before its tables may be reused.

**Protected interval**:
The per-table interval `[start, end + buffer)` during which the table is unavailable. Overlapping
active protected intervals on one table are impossible.

**Evening**:
A restaurant-local calendar date. Used for the max-seatings-per-table rule and for grouping
reservations in the admin view.

**Max seatings per table**:
At most two active reservations per table per evening, counting reservations of all sources;
staff may override this for their own bookings.

## Tables and allocation

**Table**:
A physical restaurant table with a fixed capacity.
_Avoid_: "table" for anything else (e.g. a database table) in prose

**Enclave**:
A named group of tables that may be physically joined into one larger table. Tables without an
enclave cannot be joined, and tables from different enclaves cannot be combined.

**Allocation**:
The set of one or more tables assigned to a reservation.

**Allocator**:
The component that computes allocations for new reservations, including combining tables within
an enclave and reassigning existing unlocked, unstarted reservations when needed.

**Reassignment**:
Changing an existing reservation's allocation while preserving its identity, times, customer,
and manage token. Never applied to locked or already-started reservations.

**Locked reservation**:
A reservation flagged by staff as protected from any reassignment until unlocked.

**Allocation priority**:
A per-table preference value used only as a tie-breaker; lower is preferred.

## People and access

**Customer**:
A person making a reservation. Contact information only — no account. Email is contact info,
not identity, and is not unique. Each reservation has its own customer record.
_Avoid_: user, account, guest record

**Staff user**:
A restaurant employee with access to the admin interface, scoped to their restaurant.

**Manage token**:
The secret capability that allows self-service cancellation of a reservation via its link.
Treated as a secret; shown on screen and sent once by email.
_Avoid_: cancel code, magic link

**Source**:
How a reservation was created: `online`, `phone`, or `walk_in`.

**Override reason**:
The staff-recorded justification when a staff booking departs from the standard online policies
(e.g. duration, party size, or seating-limit overrides).

**Status**:
A reservation's lifecycle state: `active` or `cancelled`.

## Time and configuration

**Restaurant**:
The single tenant of the MVP. Owns its timezone, booking horizon, opening hours, booking rules,
tables, and staff.

**Opening hours**:
Per-weekday times: `open_time`, `kitchen_close_time`, `close_time`. A weekday without an opening
hours record is closed. If `close_time` ≤ `open_time`, closing is on the following day
(e.g. 00:00 = next midnight).

**Kitchen cutoff**:
The latest allowed reservation start: strictly before `kitchen_close_time`. Applies to all
reservations, including staff bookings.

**Booking horizon**:
How far ahead of today customers may book (30 days), computed in restaurant-local time.

**Booking rules**:
The configurable rule set for a restaurant: seating windows, duration, buffer, slot interval,
max online party size, max seatings per table. Read dynamically; changes need no change to the
core reservation logic.

## Data lifecycle

**Customer note**:
Optional free-text submitted by the customer with a reservation (e.g. allergies). Visible to
staff only; never affects availability.

**Table note**:
A staff note attached to a table, optionally with an expiry. Staff-visible only; never blocks capacity.

**Anonymization**:
The retention operation that removes personal data from a reservation 90 days after cancellation
(or after the reservation date for stale reservations): customer reference, customer note, and
manage token are cleared and the customer record is deleted in one transaction, while the
reservation itself is kept for statistics.
