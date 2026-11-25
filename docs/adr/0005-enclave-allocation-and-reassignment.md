# Enclave-based allocation with automatic reassignment

Status: accepted

Tables belong to at most one enclave; only tables sharing an enclave may be combined, and tables
without an enclave are never joined. Online bookings (party ≤ 6) automatically combine tables
within one enclave when a single table's capacity is insufficient. The allocator's preference
order: (1) valid capacity and buffered availability on every candidate table, (2) preserve useful
table combinations, (3) minimize reassignment of existing reservations, (4) minimize unused seating
capacity, (5) `allocation_priority` (lower = preferred) as tie-breaker. When no static allocation
fits, the allocator may reassign existing reservations — only if unlocked and not yet started —
preserving their id, times, customer, and manage token. Started or locked reservations are never
moved; in the MVP staff manual moves are also future-only. Customers are never notified of table
changes (they never choose a table). Availability queries may simulate reassignment plans but must
never apply them; availability is re-validated inside the booking transaction.

Considered options: online single-table-only allocation (rejected: parties of 5–6 would be
unbookable given the seed floor plan); cancel+rebook for staff moves (rejected for usability;
kept for any date/time/party change).
