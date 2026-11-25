# Restaurant booking policies — updated kitchen and closing hours

## 1. Opening hours and kitchen cutoff

- `OPENING_HOURS` defines **three distinct times** in the restaurant's local timezone: `open_time` (17:30), `kitchen_close_time` (21:00), and `close_time` (00:00 = midnight on the **following day**).
- The kitchen cutoff applies to **both online and staff-created reservations**, including phone bookings and walk-ins. A reservation must **start strictly before 21:00**; arriving at 21:00 is too late.
- Occupied time must end no later than restaurant closing at 00:00 the following day. The 15-minute buffer is mandatory **between reservations**; it does not extend the guest's permitted stay beyond closing time.
- A weekday without an `OPENING_HOURS` row is closed. Availability is offered from local today through local today + `booking_horizon_days` (30), excluding past slots.
- All slot/seating calculations and local-evening grouping use `RESTAURANTS.timezone` (e.g., `Europe/Copenhagen`). `starts_at` and `ends_at` are stored as UTC `TIMESTAMPTZ` values.

**Validation (local restaurant time):**

```text
open_at <= starts_at < kitchen_closes_at
starts_at < ends_at <= restaurant_closes_at
restaurant_closes_at = next-day 00:00 when close_time = 00:00
```

## 2. Standard online seating

- First seating starts: **17:30, 17:45, 18:00, 18:15**.
- Second seating starts: **19:45, 20:00, 20:15, 20:30**. Its window is derived from the first-seating window + `reservation_duration_minutes` + `buffer_minutes`.
- Each online reservation lasts **120 minutes**, using **15-minute start intervals** and a **15-minute mandatory buffer** between table occupancies.
- If the same table is used in both seating windows, `second_start >= first_start + 135 minutes`, irrespective of which seating is booked first.
- Online allocation permits at most **two active reservations per table per local evening**, counting reservations from all sources; authorized staff may override this policy.
- Online party size is **1–6**. All reservations must also satisfy opening-hour and kitchen-cutoff restrictions.

## 3. Enclaves, allocation, and reassignment

- Tables with the same non-null `enclave_id` may be joined; tables with a null enclave cannot join, and different enclaves cannot be mixed.
- `RESERVATION_TABLE_ALLOCATIONS` assigns **one or more physical tables** to each reservation. Online allocation may combine tables within one enclave when needed for parties of up to six.
- The allocator checks total capacity and buffered availability of **every assigned table**, preferring minimal reallocations and efficient use of capacity; lower `allocation_priority` is preferred as a tie-breaker.
- The allocator may move existing **unstarted and unlocked** reservations, preserving their ID, time, customer and cancellation token. It never moves started or locked reservations.
- A move changes only table allocations. Changing reservation date/time requires cancellation and a new reservation.
- Availability queries may **simulate** feasible reassignment plans but never apply them. Availability must be checked again when a booking transaction is committed.

## 4. Staff bookings and locks

- Staff phone and walk-in bookings may override standard seating windows, the 15-minute grid, 120-minute duration, online party-size limit, and maximum-two-seatings policy. Any deviation should be recorded in `override_reason`.
- Staff cannot override the kitchen cutoff (start strictly before 21:00), restaurant closing time (guests leave by midnight), table capacity, table conflicts or the 15-minute buffer.
- Staff can combine physically compatible tables from the same enclave; staff members judge whether combinations are physically suitable.
- Only authorized staff may set `RESERVATIONS.is_locked`. Locked reservations cannot be moved until unlocked. Staff may manually reassign **unstarted, unlocked** reservations.
- Online reservations use `source='online'`, a customer row, and a cancellation token. Staff-created phone/walk-in reservations record `created_by_staff_id`; anonymous walk-ins may have `customer_id=NULL` and `manage_token=NULL`.

## 5. Integrity and concurrency

- Every booking runs in a transaction. Lock affected table rows in a consistent order, validate the complete allocation plan, then commit all allocation changes together; roll back on conflict.
- A PostgreSQL `EXCLUDE` constraint prevents overlap of active allocations' protected ranges (`protected_from = starts_at`, `protected_until = ends_at + buffer_minutes`); cancelled allocations do not block capacity.
- Enforce valid table/restaurant relationships, enclave compatibility, party-size capacity, allowed `status` (`active`, `cancelled`) and `source` (`online`, `phone`, `walk_in`) values.
- Maintain `RESERVATION_TABLE_ALLOCATIONS.is_active` and protected ranges transactionally with reservation state and timing.

## 6. Customer confirmations and notes

- Online customers provide contact information in a **new customer row per reservation**. Email is not unique, and customers do not need accounts.
- Customers may add an optional `customer_note`. Staff may attach `TABLE_NOTES` to physical tables, optionally with `expires_at`. Notes do not directly block availability.
- Send one confirmation email through Resend after a successful booking, with a unique cancellation link. Always show the confirmation and link on screen, even if email delivery fails. `email_sent_at` records successful provider acceptance, not an attempted send.

## 7. Data retention

- A scheduled job processes cancelled reservations **90 days after cancellation**, or completed/stale reservations **90 days after their reservation date**.
- For each due reservation, clear `customer_note` and `manage_token`, set `customer_id=NULL` and `anonymized_at`, and **delete** its dedicated customer row in the same transaction. Retain non-personal booking records for audit/statistics.
- Delete expired `TABLE_NOTES` automatically. Check constraints must permit the null customer/token fields after anonymization.
