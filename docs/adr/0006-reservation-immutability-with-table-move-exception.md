# Reservations are immutable except for table allocation

Status: accepted

After creation, the only mutable part of a reservation is its table allocation. A staff move is an
atomic in-place allocation update inside a locked transaction that validates availability first,
preserving the reservation's id, times, customer, and manage token. Any change to date, time, or
party size is a cancellation plus a new reservation (the original stays as `cancelled` for audit).
This refines the original PRD §14.4 ("no edits after creation"): the exception is deliberate, so
staff can react to no-shows and physical constraints without losing the reservation's identity or
its customer's cancellation link.
