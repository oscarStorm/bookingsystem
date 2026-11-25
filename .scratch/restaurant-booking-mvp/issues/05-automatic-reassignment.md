# 05: Automatic reassignment of unlocked, unstarted reservations

**What to build:** The allocator's reassignment capability per ADR-0005: when no conflict-free candidate exists without moving existing reservations, unlocked and not-yet-started reservations may be reassigned — allocations only, with id, times, customer, and manage_token preserved; started or locked reservations are never moved; customers are never notified. Preference order: validity → preserve useful table combinations → minimize reassignments → minimize unused seating capacity → allocation_priority (lower first). Availability queries may simulate reassignment plans but never apply them; every plan is re-validated inside the booking transaction before commit.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] A booking succeeds by reassigning an unlocked, unstarted reservation; the moved reservation keeps id, times, customer, and token
- [ ] Locked or already-started reservations are never reassigned (integration test)
- [ ] Availability reflects simulated reassignment without persisting it — no allocation rows change on a GET
- [ ] Concurrency test: booking while a reassignment plan is needed → exactly one winner, 409 for the loser
