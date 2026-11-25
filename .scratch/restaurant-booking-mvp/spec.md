# Spec — Restaurant Booking System MVP

Status: ready-for-agent

Source of truth for all decisions below: `prd/PRD2.md` (settled in design review), `database-diagram/booking_policies.2.0.md`, `database-diagram/ER-diagram.2.0.svg`. The repo currently contains docs only — this spec covers building the MVP from scratch.

## Problem Statement

The restaurant handles table reservations manually, which causes double bookings, no overview of the evening, and administrative overhead. Customers cannot book online, and staff have no protected tool to view, create, cancel, or relocate reservations. There is no reliable enforcement of seating windows, kitchen cutoff, buffers, or table capacity.

## Solution

A fullstack MVP web application: customers book tables online through a Svelte SPA served by a FastAPI backend (SQLAlchemy 2.x + Pydantic + Alembic) on PostgreSQL. The backend computes availability from configurable booking rules (seating windows, duration, buffer, opening/kitchen hours, horizon), auto-allocates tables (single best-fit or combined within an enclave, with automatic reassignment of unlocked future reservations), and guarantees no double bookings via row locks + a PostgreSQL EXCLUDE constraint. Staff administer reservations through a cookie-authenticated admin UI (view per date, create phone/walk-in bookings with overrides, cancel, move tables, lock, table notes). Customers get an on-screen confirmation with a self-service cancellation link plus one confirmation email (Resend). Customer PII is anonymized by a scheduled 90-day retention job. Deployed as a multi-stage Docker image on Render (Neon PostgreSQL, Frankfurt), CI-gated by pytest on protected `main`.

## User Stories

**Customer-facing**
1. As a customer, I want to pick a date within the 30-day booking horizon, so that I can plan a visit but not book arbitrarily far ahead.
2. As a customer, I want to enter a party size of 1–6, so that the system can find a table with sufficient capacity.
3. As a customer, I want to see only bookable start times (15-minute grid within the first seating window 17:30–18:15 and the derived second window 19:45–20:30, within opening hours, starting strictly before the 21:00 kitchen cutoff, excluding past slots and closed days such as Monday), so that I never pick an impossible slot.
4. As a customer, I want availability to reflect all existing active reservations (online, phone, walk-in), the 15-minute buffer, and table capacity — including enclave-combined options — so that I am never promised an unavailable table.
5. As a customer, I want the system to assign the table automatically (I never choose a table), preferring capacity-efficient arrangements and minimizing disruption to existing reservations, so that the floor is used optimally.
6. As a customer, I want to enter my name, email, and phone, plus an optional free-text note (e.g. allergies), so that the restaurant can contact me and prepare appropriately.
7. As a customer, I want an on-screen confirmation showing date, time, party size, and a cancellation link, so that I have immediate proof of the booking.
8. As a customer, I want one confirmation email containing the same cancellation link, so that I can cancel later even after leaving the site.
9. As a customer, I want to cancel my reservation via the link without an account, so that the table becomes available again.
10. As a customer, I want a clear error with alternative slots if my chosen slot was taken between viewing and submitting (HTTP 409), so that I can pick another time.
11. As a customer, I want clear validation errors for invalid input (bad email, party size out of range, note too long), so that I can correct my submission.
12. As a customer wanting to book for more than 6 people, I want to be told to contact the restaurant by phone/email, so that large parties are handled manually.
13. As a customer, I want closed weekdays to show no availability, so that I don't attempt to book on a closed day.

**Staff-facing**
14. As a staff member, I want to log in with email and password, so that only authorized users reach the admin area.
15. As a staff member, I want to see all reservations for a chosen date with time, party size, customer contact, note, source, table allocation, and lock status, so that I have an overview of the evening.
16. As a staff member, I want to create a reservation manually (phone or walk-in) at arbitrary times, overriding seating windows, the 15-minute grid, the 120-minute duration, the party-size limit, and the two-seatings limit, with the deviation recorded as an override reason — while never overriding the kitchen cutoff, closing time, capacity, conflicts, or the buffer.
17. As a staff member, I want walk-in reservations to be allowed without contact details (anonymous) and without a cancellation token.
18. As a staff member, I want to cancel a reservation, so that its capacity is freed immediately in the same transaction.
19. As a staff member, I want to move an unstarted, unlocked reservation to different table(s) atomically, preserving its id, times, customer, and cancellation token, so that the floor plan can be adjusted safely.
20. As a staff member, I want to lock a reservation, so that the automatic allocator never moves it; unlocking restores movability.
21. As a staff member, I want to attach notes to a table (with optional expiry), visible to staff only and never blocking capacity, so that I can record e.g. broken chairs or event reservations.

**System-facing**
22. As the system, I want to prevent any overlapping protected intervals per table at the database level (EXCLUDE constraint on active allocations' protected range = [starts_at, ends_at + buffer)), so that double booking is impossible even if application logic fails.
23. As the system, I want to serialize concurrent booking attempts on the same tables (transaction + row locks in sorted order, re-validate, commit; rollback on conflict), returning 409 to losing requests, so that simultaneous bookings never double-book.
24. As the system, I want to compute availability independently of booking order and to simulate (never apply) reassignment of unlocked, unstarted reservations when answering availability queries, re-validating everything inside the booking transaction, so that displayed slots are exactly bookable and booking order never restricts customers.
25. As the system, I want to enforce the max-two-active-reservations-per-table-per-evening rule counting all sources (staff may override), and the pair rule second_start ≥ first_start + 135 minutes when one table is used in both seating windows.
26. As the system, I want to send exactly one confirmation email per reservation after the database commit, recording provider acceptance, never letting email failure block or invalidate a booking, and always showing the cancellation link on screen.
27. As the system, I want to treat the manage_token as a secret bearer capability for cancellation.
28. As the system, I want a scheduled job that, 90 days after cancellation (or 90 days after the reservation date for completed/stale reservations), clears customer note and token, nulls the customer reference, stamps anonymized_at, deletes the dedicated customer row in one transaction, and deletes expired table notes — preserving the reservation row for statistics.
29. As the system, I want all slot/seating/evening math in the restaurant's local timezone (Europe/Copenhagen) with UTC timestamptz storage.

## Implementation Decisions

- **Stack:** FastAPI backend; SQLAlchemy 2.x models with separate Pydantic schemas (explicit control over relationships, transactions, PostgreSQL-specific constraints — deliberately not SQLModel); Alembic migrations; PostgreSQL 16; Svelte SPA built with Vite; multi-stage Docker (Node build stage → dist served by FastAPI via StaticFiles on the same service); vanilla HTML fallback only if Svelte slips.
- **Backend layering:** api (REST endpoints) / config / schemas (DTOs+validation) / models (SQLAlchemy entities) / repositories (all persistence queries) / services (business logic and rules; services own the transaction boundary — begin, lock, validate, commit, rollback) / security (auth) / database (engine, sessions). Migrations for schema only; demo seed data in a separate idempotent seed script; retention logic in a service with a separately runnable cleanup script; k6 perf tests under the backend perf tests area.
- **Schema (10 tables):** restaurants; booking_rules (1:1 per restaurant); opening_hours (per weekday: open_time, kitchen_close_time, close_time — close ≤ open means next-day closing, e.g. 00:00 = next midnight; no row = closed day); table_enclaves; restaurant_tables (enclave_id nullable, capacity, allocation_priority lower=preferred, is_active); staff_users (email unique, Argon2id hash); customers (email NOT unique; one dedicated row per reservation); reservations (customer_id nullable w/ ON DELETE SET NULL, created_by_staff_id nullable, starts_at/ends_at timestamptz, party_size, status ∈ {active, cancelled}, source ∈ {online, phone, walk_in}, is_locked, customer_note, override_reason, manage_token uuid unique nullable, email_sent_at, anonymized_at, cancelled_at); reservation_table_allocations (reservation_id+table_id PK, protected_from, protected_until, is_active); table_notes (table_id, staff_id, content, expires_at nullable).
- **Integrity:** UNIQUE(booking_rules.restaurant_id); UNIQUE(tables(restaurant_id, table_number)); UNIQUE(enclaves(restaurant_id, name)); UNIQUE(staff email); UNIQUE(manage_token) when populated; CHECKs: party_size>0, capacity>0, ends_at>starts_at, expires_at>created_at when present, status/source enums; online ⇒ created_by_staff_id NULL AND manage_token set; staff-created ⇒ created_by_staff_id set AND manage_token NULL. EXCLUDE USING gist (table_id =, tstzrange(protected_from, protected_until) &&) WHERE is_active on allocations (requires btree_gist extension). All allocation table/enclave ids must belong to the reservation's restaurant.
- **Booking rules (seed):** first_seating_start 17:30, first_seating_last_start 18:15, duration 120, buffer 15, slot interval 15, max online party size 6, max seatings per table 2, horizon 30 days. Second window derived: [first_start + duration + buffer, first_last_start + duration + buffer] = 19:45–20:30. All rules read dynamically from booking_rules; buffer changes grandfather existing allocations (protected_until computed at insert).
- **Hours (seed):** Monday closed (no row); Tue–Sun open 17:30, kitchen_close 21:00, close 00:00. Validation in local time: open ≤ start < kitchen_close; start < end ≤ close. Kitchen cutoff applies to staff bookings too; buffer never extends stay past closing.
- **Allocation algorithm:** candidate = single table or same-enclave combination with total capacity ≥ party size; every candidate table's protected interval must be free. Preference order: (1) valid capacity/availability, (2) preserve useful table combinations, (3) minimize reassignment of existing unlocked, unstarted reservations, (4) minimize unused seating capacity, (5) allocation_priority tie-breaker (lower preferred). Reassignment changes only allocations — id, times, customer, token preserved; never moves started or locked reservations; customers are never notified. Availability queries may simulate reassignment plans but never apply them.
- **Concurrency:** every booking/cancel/move runs in one transaction: lock affected table rows with SELECT … FOR UPDATE in sorted order, re-read reservations, validate (windows, locks, capacity, enclave, duration, buffered availability, max-2), apply allocation changes + reservation atomically, commit; rollback on conflict; EXCLUDE violation → HTTP 409 with alternative slots.
- **Immutability:** after creation only the table allocation may change (staff move, atomic, future+unlocked only in MVP). Date/time/party changes = cancel + rebook (new id + token; original kept as cancelled for audit).
- **Auth:** staff email+password, Argon2id, HTTP-only signed cookie session (no JWT); single role for MVP; staff scoped to their restaurant_id; is_locked writable only via staff endpoints (app-level).
- **Email:** Resend, API key in env vars only; one confirmation email after commit containing details + cancellation link; email_sent_at records provider acceptance (idempotent resend protection); failure never blocks the booking; on-screen confirmation always shows the link; no allergy/sensitive note content in emails.
- **API surface (contracts):** GET /api/availability?date&party_size → sorted bookable start times; POST /api/reservations → 201 with reservation + manage_token/cancellation link, 400 invalid input, 409 conflict with alternative slots; GET/POST cancellation by manage_token (public); POST /api/auth/login + logout (cookie); GET /api/admin/reservations?date (auth); POST /api/admin/reservations (staff create w/ overrides + override_reason); POST /api/admin/reservations/{id}/cancel; POST /api/admin/reservations/{id}/move {table_ids}; POST lock/unlock; table notes CRUD (auth); GET /health.
- **Deployment:** .env (gitignored) + .env.example locally; DATABASE_URL + email + secret-key env vars on Render; merge to main → GHA pytest → Render Docker build → pre-deploy alembic upgrade head → live HTTPS; branch protection with green-PR requirement; free-tier cold start (30–60 s) documented as accepted MVP limitation.
- **Seed data (idempotent script):** restaurant id=1 "Demo Restaurant", Europe/Copenhagen, horizon 30; enclaves: 1 "Enclave 1" (combined cap 6), 2 "Enclave 2" (combined cap 4); tables: #1 cap 4 enclave NULL priority 40; #2 cap 2 NULL 10; #3 cap 2 E1 30; #4 cap 2 E1 31; #5 cap 2 E1 32; #6 cap 2 E2 20; #7 cap 2 E2 21; opening hours per above; booking rules per above; one staff account admin@demo-restaurant.example, role admin, Argon2id hash of a password supplied via environment variable (never hardcoded).
- **Requirement priorities:** Must — availability/booking/cancel core (F-01…F-09, F-20 self-cancel), enclave combining (F-17), automatic reassignment (F-18), staff manual bookings (F-10); Should — confirmation email (F-13), is_locked (F-19), manual table move (F-14); Could — customer note (F-15), table notes (F-16); deferred entirely — general editing (F-11), admin settings UI (F-12, config via seed instead).
- **Performance:** NF-09 — warm p95 < 1 s under k6: 50 virtual users, 5 minutes, availability lookups + booking attempts, test database, emails disabled; cold starts excluded.

## Testing Decisions

- **Principle:** test external behavior, not implementation details; prefer the highest seam. Greenfield repo — no prior art; establish the pattern: pure-logic unit tests around services, API-level integration/e2e through FastAPI + real database.
- **Unit (services, no DB):** seating-window and slot-grid generation, derived second window, pair rule (135 min), kitchen-cutoff/closing validation, buffer/protected-interval computation, allocator preference order (combos, minimize moves, capacity efficiency, priority tie-break), timezone/evening grouping, horizon/closed-day filtering.
- **Integration (API + DB, incl. migrations):** reservation creation persists reservation + allocations; availability reflects existing bookings from all sources; cancelled reservations free capacity; EXCLUDE constraint rejects overlaps; enclave rules (NULL unjoinable, cross-enclave forbidden); CHECK/enum constraints; override rules for staff bookings; anonymized rows satisfy nullable constraints.
- **Concurrency tests:** two simultaneous bookings for the same table/slot → exactly one 201, one 409; simultaneous cancels; booking while a reassignment plan would be needed.
- **E2E:** full customer flow (date → party size → slots → details → confirmation + link → self-cancel); staff flow (login → list by date → create walk-in with override → move table → lock → cancel); closed day; party > 6 message; 409 alternative-slots flow.
- **Performance:** k6 script (50 VU, 5 min, mixed availability + booking, test DB, emails disabled), warm p95 < 1 s assertion, run documented.
- **Retention job test:** fixture reservations 91 days past cancellation/date → job nulls PII fields, sets anonymized_at, deletes customer row, deletes expired table notes, single transaction, reservation rows preserved.
- **CI:** pytest runs on every PR and merge to main; main protected — merge only via green PRs.

## Out of Scope

- SMS and all automated emails except the single confirmation email (no reminders, cancellation notifications, or reassignment notices).
- Customer accounts / loyalty; statistics and reporting UI (reservation rows retained for future statistics).
- Multi-restaurant UI / tenant management (schema keeps restaurant_id everywhere; exactly one restaurant seeded; all queries filtered by it).
- Drag-and-drop floor plan; combining tables across enclaves or with enclave_id NULL.
- Editing date/time/party size after creation (cancel + rebook); general editing (F-11); admin settings UI (F-12) — configuration via seed data.
- Reassignment (automatic or manual) of reservations whose start time has passed.
- Notifying customers of table changes.
- Paid Render instance guarantees; cold-start latency is accepted and documented for the MVP.

## Further Notes

- `prd/PRD2.md` is the consolidated decision record from the design review; `prd/PRD.md` is the preserved original draft.
- Doc drift to fix alongside implementation: `deployment/deployment-plan.md` still says SQLModel and "7 ER tables" (now SQLAlchemy 2.x, 10 tables, new backend layout, seed/cleanup scripts); old `ER-diagram.png` / `restaurant_booking_policies*.md` are superseded by `ER-diagram.2.0.svg` / `booking_policies.2.0.md`; GLOSSARY.md and docs/adr entries for the hard-to-reverse decisions (concurrency model, enclave allocation, immutability-with-table-move, kitchen cutoff, email-in-scope, retention, SQLAlchemy-over-SQLModel) are still to be written.
- Naming: the ER column is `max_online_party_size` (an earlier note said `max_party_size` — ER name is canonical).
- Secrets (DATABASE_URL, Resend key, session secret, seed admin password) live only in env vars / Render dashboard — never in Git.
