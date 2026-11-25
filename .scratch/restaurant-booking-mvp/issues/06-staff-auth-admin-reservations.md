# 06: Staff authentication and admin reservation management

**What to build:** Staff auth per ADR-0010 — email + password, Argon2id hash, HTTP-only cookie session (no JWT), single role for the MVP, staff scoped to their restaurant_id, login/logout endpoints. Plus the admin reservation API: per-date list showing time, party size, customer contact, note, source, table allocation, and lock status; staff create (phone/walk-in) that may override seating windows, the 15-minute grid, the duration, the party-size limit, and the two-seatings limit — recorded as override_reason — while never overriding the kitchen cutoff, closing time, capacity, buffer, or conflicts; walk-ins may be anonymous (no contact details, no token); staff cancel; and lock/unlock (is_locked writable only via staff endpoints).

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] Login sets an HTTP-only cookie; admin endpoints reject unauthenticated requests; staff are scoped to their own restaurant
- [ ] Staff create with override_reason persists and appears in the date list; override attempts on kitchen cutoff, closing time, capacity, buffer, or conflicts are rejected
- [ ] Anonymous walk-in reservation has no customer row and no manage_token
- [ ] Staff cancel frees capacity in the same transaction; locking prevents later allocator moves, unlocking restores movability
