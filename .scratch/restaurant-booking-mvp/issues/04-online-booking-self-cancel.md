# 04: Online booking and self-service cancellation

**What to build:** The customer write path: `POST /api/reservations` → 201 with the reservation and a manage_token cancellation link, 400 on invalid input (bad email, party size out of range, note too long; parties above the max online party size get a "contact the restaurant" message), 409 with alternative slots on conflict. Booking transaction discipline per ADR-0002: begin, lock affected table rows with SELECT … FOR UPDATE in sorted order, re-read and re-validate everything (windows, kitchen cutoff, capacity, enclave, duration, buffered availability, max-2), apply reservation + allocation rows atomically, commit; an EXCLUDE violation maps to 409. Auto-allocation picks the best candidate (single table or same-enclave combination) preferring capacity efficiency, preserving useful combinations, with allocation_priority as tie-breaker. One dedicated customer row per reservation; the manage_token is a secret bearer capability. Public GET/POST cancellation by token frees the capacity in the same transaction.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] Integration: creation persists the reservation and its allocation rows; token-based cancellation frees capacity immediately
- [ ] Concurrency: two simultaneous bookings for the same table/slot → exactly one 201 and one 409 with alternative slots; simultaneous cancels are safe
- [ ] E2E: customer books → on-screen confirmation with cancellation link → self-cancel via token; invalid input → 400 with field errors
