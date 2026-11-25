# Concurrency model: sorted row locks + PostgreSQL EXCLUDE constraint

Status: accepted

Every booking, cancellation, and table move runs in one database transaction that locks all
affected table rows with `SELECT … FOR UPDATE` in a consistent sorted order, re-validates the
full allocation plan (seating rules, lock status, capacity, enclave compatibility, buffered
availability, max seatings), then commits all changes atomically; any conflict rolls back and the
client gets HTTP 409. On top of that, a database-level `EXCLUDE USING gist (table_id WITH =,
tstzrange(protected_from, protected_until) WITH &&) WHERE (is_active)` on the allocation table is
the hard guarantee that overlapping protected intervals can never be committed, even if
application logic is buggy. Requires the `btree_gist` extension. `protected_until` is computed
from the booking rules at insert time, so later buffer changes grandfather existing allocations.

Considered options: application-level locking only (rejected: a bug could double-book); EXCLUDE
constraint only (rejected: the max-2-seatings count and friendly 409 need serialized validation
under the lock anyway).
