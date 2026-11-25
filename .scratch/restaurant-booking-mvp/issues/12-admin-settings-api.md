# 12: Admin settings API (tables, opening hours, booking rules)

**What to build:** Staff-scoped CRUD endpoints plus validation logic for restaurant configuration: restaurant tables (capacity, enclave, allocation priority, active flag), opening hours (open, kitchen close, close per weekday, including next-day closing), and booking rules (seating windows, duration, buffer, slot interval, max online party size, max seatings per table, booking horizon, closed days). Validation includes refusing inconsistent hours (start ≥ kitchen close) and refusing to shrink a table below existing reservations. Crucially, the allocator and availability must read all rules dynamically from the database — no booking-rule values hardcoded in reservation logic. UI is deferred until the Figma exists; the endpoints must exist and be tested.

**Blocked by:** 02, 06.

**Status:** ready-for-agent

- [ ] Changing a booking rule via the API changes availability output with no code change (proven by pytest)
- [ ] Invalid configurations are rejected with clear errors (e.g. start ≥ kitchen close, table capacity below existing reservations)
- [ ] Endpoints require staff authentication and are scoped to the staff member's restaurant
