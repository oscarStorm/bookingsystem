# 03: Seating model and availability API

**What to build:** The read-only availability path: `GET /api/availability?date&party_size` returning sorted bookable start times. Slot generation reads booking_rules dynamically from the database: first seating window on the configured 15-minute grid, the derived second window (first_start + duration + buffer … first_last_start + duration + buffer), reservation duration, buffer, slot interval, booking horizon, and closed weekdays (no opening_hours row ⇒ no slots). Validation in restaurant local time: open ≤ start < kitchen_close (kitchen cutoff applies to all sources), start < end ≤ close, with close ≤ open meaning next-day closing (00:00 = next midnight). Availability reflects all active reservations from every source, buffered protected intervals, table capacity including same-enclave combinations (enclave_id NULL is never combinable, cross-enclave forbidden), max two active reservations per table per local evening, and the pair rule second_start ≥ first_start + 135 minutes. All slot math in the restaurant's local timezone with UTC timestamptz storage.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] Unit tests cover: slot grid generation, derived second window, pair rule, kitchen-cutoff and closing validation, buffer/protected-interval computation, closed-day and horizon filtering, timezone handling
- [ ] Integration tests: availability shrinks correctly when reservations exist (all sources counted), enclave-combined capacity appears, max-2-seatings per table per evening is enforced
- [ ] Closed Monday and dates beyond the horizon return no slots
