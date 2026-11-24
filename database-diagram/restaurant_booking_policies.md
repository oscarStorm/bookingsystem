# Restaurant booking policies — enclave-aware allocation

## 1. Seating rules (online)

- First seating starts: **17:30, 17:45, 18:00, 18:15**.
- Second seating starts: **19:45, 20:00, 20:15, 20:30**. Its fixed window is derived from the earliest/last first-seating starts plus the 120-minute duration and 15-minute buffer.
- Each reservation lasts **120 minutes**, and a **15-minute buffer** is mandatory after occupied time.
- If both seating windows are used by the same table, `second_start >= first_start + 135 minutes`.
- Standard online allocation allows at most **two active reservations per table per local evening** (all sources count); staff can override this limit.
- Online party size is **1–6**. Booking times must fit restaurant opening hours, the local booking horizon, and 15-minute intervals.

## 2. Enclaves and automatic allocation

- A table with `enclave_id = NULL` is **not joinable**. Tables sharing the **same non-NULL enclave** may be joined to form one reservation; different enclaves cannot be combined.
- `RESERVATION_TABLE_ALLOCATIONS` maps one reservation to one or more tables. **Online bookings may automatically combine tables within one enclave**, subject to the six-guest limit and sufficient total capacity.
- The allocator considers single-table and compatible combined-table options, checks the protected intervals for **every** table, and uses `allocation_priority` as an allocation preference / tie-breaker.
- To preserve usable capacity, the allocator may search for **reassignments of existing unseated, unlocked reservations** before rejecting a new booking. Existing reservations keep their `id`, times, `customer_id`, and `manage_token`; only table allocations change.
- **Minimize unnecessary moves.** Prefer an allocation requiring fewer changes when viable; within comparable options, prefer capacity-efficient arrangements and configured allocation priorities.
- When no legal arrangement exists, the system reports that the slot is unavailable.

## 3. Staff overrides and locks

- Staff bookings (`phone`, `walk_in`) may bypass standard seating windows, time-grid, party-size limit, 120-minute duration, and two-seat limit.
- Staff **cannot** bypass table occupancy, physical capacity, or the **15-minute buffer**. Staff can manually combine tables within one enclave.
- `RESERVATIONS.is_locked BOOLEAN NOT NULL DEFAULT FALSE` is **only writable by authorized staff**. A locked reservation must not be reallocated automatically or manually until staff unlock it; the customer cannot set the flag.
- Staff-created reservations are **not automatically locked**; staff choose whether to lock them. A reservation whose start time has passed is never auto-moved; staff should lock any party seated ahead of schedule.
- Staff overrides should be recorded in `override_reason` when they depart from the normal online booking policies.

## 4. Atomicity and database safeguards

1. Begin a database transaction; lock all affected tables in a consistent sorted order (`SELECT ... FOR UPDATE`).
2. Re-read affected reservations and validate seating rules, lock status, capacity, enclave compatibility, duration, and buffered availability.
3. Atomically update any unlocked existing table allocations and insert the new reservation/allocations.
4. Commit. On conflict, roll back without changing existing reservations.

- PostgreSQL `EXCLUDE` on the active allocation's `(table_id, protected time range)` prevents overlapping occupied + buffered intervals. Cancelled allocations are excluded.
- All table IDs in an allocation must belong to the same restaurant as the reservation; enclave IDs must belong to that restaurant too.
- `UNIQUE(restaurant_id, table_number)` and `UNIQUE(restaurant_id, enclave name)` keep names/numbers scoped per restaurant.
- No online customer may alter table assignments or `is_locked`.

## 5. Existing customer and staff features (unchanged)

- Online customers provide contact information (`CUSTOMERS.email` **not unique**), can add an optional `customer_note`, receive a confirmation email and on-screen cancellation link via `manage_token`.
- Staff may record `TABLE_NOTES` with optional expiry; notes do not block availability.
- Reservations are not edited for date/time; staff may reassign **tables only**, preserving reservation identity and token. Changing date/time requires cancel + rebook.
- Reservations use local restaurant time for seating windows/evenings and UTC `TIMESTAMPTZ` for storage.
