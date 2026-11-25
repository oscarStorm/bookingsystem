# Product Requirements Document v2 (PRD2) — Restaurant Booking System

**Project:** Restaurant Booking System ("Jubilee")
**Version:** 2.0 – decisions settled in design review
**Status:** Supersedes `prd/PRD.md` (v0.1 draft, preserved for history)
**Project type:** Fullstack web application, MVP

This document consolidates every decision reached in the design review (grilling session).
Where it conflicts with `PRD.md`, this document wins. Source of truth for seating/allocation
policy details: `database-diagram/booking_policies.2.0.md` + `database-diagram/ER-diagram.2.0.svg`.
Domain vocabulary: `GLOSSARY.md`; hard-to-reverse decisions: `docs/adr/`.

---

## 1. Product description

A web-based booking system where **customers** reserve tables online and **restaurant staff**
administer reservations through a protected admin interface. The system prevents double
bookings, computes availability from configurable seating rules, and is deployed as a
containerized FastAPI + PostgreSQL application.

## 2. Target groups

- **Customers:** see availability, book 1–6 guests, receive on-screen confirmation + confirmation
  email with a self-service cancellation link. No account required.
- **Staff:** log in, view/create/cancel reservations, move a reservation to another table,
  create phone/walk-in bookings with overrides, add table notes.

## 3. Scope

### 3.1 In scope — MVP

- Web UI (customer booking + staff admin), REST API, relational database
- Availability computation and double-booking prevention (DB-enforced)
- Create / cancel reservations; customer self-cancel via `manage_token` link
- Confirmation email containing the cancellation link (one email per reservation)
- Protected admin interface (cookie session)
- Configurable tables, opening hours and booking rules — stored in DB, seeded via an idempotent
  seed script kept separate from schema migrations, read dynamically by the backend (no hardcoding)
- Enclave-based automatic table allocation, including automatic combining of tables within one
  enclave for online bookings, and allocator-driven reassignment of unlocked future reservations
- Staff table reassignment of existing reservations (in place, atomic)
- Automated tests (unit, integration, concurrency, e2e) + CI gate before merge
- Deployment: Docker → Render, PostgreSQL on Neon, Alembic migrations on deploy

### 3.2 Out of scope — MVP

- SMS and all other automated emails (reminders, cancellation notifications, reassignment notices)
- Customer accounts and loyalty programs
- Statistics and advanced reporting (reservation rows are kept for future statistics)
- Multi-restaurant UI / tenant management (schema is multi-restaurant-ready; MVP seeds one restaurant)
- Drag-and-drop floor plan
- Combining tables across different enclaves; joining tables with `enclave_id = NULL`
- Editing a reservation's date, time, or party size after creation (cancel + rebook instead)
- General reservation editing (F-11) and admin settings UI (F-12) — both deferred

## 4. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| F-01 | Customer selects date and party size | Must |
| F-02 | System shows available start times for that date/party size | Must |
| F-03 | Customer creates a reservation (name + contact, optional note) | Must |
| F-04 | System prevents double bookings (incl. concurrent requests → 409) | Must |
| F-05 | On-screen confirmation with reservation details **and cancellation link** | Must |
| F-06 | Staff login (email + password, cookie session) | Must |
| F-07 | Staff views reservations, filterable by date | Must |
| F-08 | Staff cancels a reservation | Must |
| F-09 | Tables, opening hours, booking rules configurable via DB seed; read dynamically | Must |
| F-10 | Staff creates manual bookings (phone / walk-in) with policy overrides | Must |
| F-11 | General reservation editing | Could (deferred) |
| F-12 | Restaurant settings editable in admin UI | Could (deferred; seed instead) |
| F-13 | Confirmation email with `manage_token` cancellation link, sent once after commit; delivery failure never blocks the booking | Should |
| F-14 | Staff reassigns a reservation's table(s) in place — one transaction, locks tables, validates availability; preserves reservation id and manage_token | Should |
| F-15 | Customer optional free-text note (`customer_note`), visible to staff | Could |
| F-16 | Staff notes on tables (`TABLE_NOTES`, optional expiry; never block capacity) | Could |
| F-17 | Automatic allocation: best-fit single table or combined tables within one enclave (online, ≤ 6 guests) | Must |
| F-18 | Allocator may reassign tables of existing **unlocked, not-yet-started** reservations to make room, minimizing moves | Must |
| F-19 | `is_locked` flag — staff-only, protects a reservation from (auto) reassignment | Should |
| F-20 | Customer self-cancel via manage_token link (no account) | Must |

Final ranking (design review round 5): Must = F-01–F-10, F-17, F-18, F-20; Should = F-13, F-14,
F-19; Could = F-15, F-16 (F-11/F-12 deferred). The allocator respects `is_locked` from the start,
even if the locking UI ships later.

## 5. Use cases

- **UC-01 Create reservation (customer):** pick date + party size → system shows available
  start times → pick time → enter name/contact (+ optional note) → confirm → system re-checks
  availability under lock → reservation + allocations committed → on-screen confirmation with
  cancellation link + confirmation email sent after commit. Alt flows: slot gone → 409 with
  alternative slots; invalid input → 400; party > 6 → "contact us" message.
- **UC-02 View reservations (staff):** login → pick date → list with time, party size, customer
  contact, note, source, table allocation, lock status.
- **UC-03 Cancel reservation (staff):** find reservation → confirm → status `cancelled` +
  allocations deactivated in one transaction → capacity freed.
- **UC-04 Self-cancel (customer):** open cancellation link (`manage_token`) → confirm →
  same transactional cancellation as UC-03. Token treated as a secret.
- **UC-05 Move reservation to another table (staff):** select reservation → choose new
  table/time-independent allocation → backend locks affected tables in sorted order, validates
  availability/capacity/enclave → updates `RESERVATION_TABLE_ALLOCATIONS` in place → commit.
  Reservation keeps id, times, customer, token. Date/time changes are NOT possible here —
  cancel + rebook.
- **UC-06 Staff booking (phone/walk-in):** staff creates reservation at arbitrary time with
  overrides (duration, party size, seating limit) recorded in `override_reason`. Walk-ins may be
  anonymous (`customer_id` NULL, `manage_token` NULL). Staff cannot bypass occupancy, capacity,
  or the 15-minute buffer.

## 6. Acceptance criteria

- **AC-01 (F-03):** reservation with valid input is stored; confirmation shown; invalid input rejected with 400.
- **AC-02 (F-04):** no table has overlapping active protected intervals `[starts_at, ends_at + buffer)`;
  enforced by PostgreSQL `EXCLUDE` + `SELECT … FOR UPDATE` transaction; two concurrent requests for the
  same slot → exactly one succeeds, the other gets 409; cancelled reservations free capacity immediately.
- **AC-03 (F-02, F-09):** only feasible start times shown — 15-min grid within both seating windows,
  within opening hours, within booking horizon, capacity (single or enclave-combined) sufficient,
  existing reservations (all sources) counted, booking-order independent (B-11).
- **AC-04 (F-06–F-08):** only authenticated staff reach admin endpoints; reservations retrievable per
  date; cancellation reflected in DB and availability.
- **AC-05 (F-13):** exactly one confirmation email per reservation (idempotent via `email_sent_at`);
  email failure leaves the reservation valid and the link on screen.
- **AC-06 (F-14, §14.4):** reservations immutable except table allocation; staff move is atomic and
  rollback preserves the original allocation; date/time change requires cancel + rebook.
- **AC-07 (retention):** the 90-day anonymization job nulls PII and deletes the customer row in one
  transaction, preserving the reservation row.

## 7. Business rules

| ID | Rule |
|---|---|
| B-01 | On an open weekday a reservation must start at or after `open_time` and **strictly before `kitchen_close_time`**, and end by `close_time`. The kitchen cutoff applies to ALL reservations, including staff bookings. The buffer never extends a stay past closing. If `close_time` ≤ `open_time`, closing is the following day (00:00 = next midnight). A weekday with no `OPENING_HOURS` row is closed. |
| B-02 | Online bookings: 1–6 guests (`max_online_party_size`). Larger parties are directed to phone/email contact. |
| B-03 | Allocation must provide aggregate capacity ≥ party size — one table, or several tables in the same enclave. |
| B-04 | Online reservation duration is 120 min (`reservation_duration_minutes`); staff may override with `override_reason`. |
| B-05 | Online starts on a 15-min grid (`slot_interval_minutes`) within the seating windows: first window = `[first_seating_start, first_seating_last_start]` (17:30–18:15); second window derived = `[first_seating_start + duration + buffer, first_seating_last_start + duration + buffer]` (19:45–20:30). |
| B-06 | 15-min buffer after every reservation: protected interval per table = `[starts_at, ends_at + buffer_minutes)`. |
| B-07 | No overlapping active protected intervals per table — DB `EXCLUDE` constraint + locked transaction; conflict → HTTP 409. |
| B-08 | Cancellation sets `status='cancelled'` and deactivates allocations in the same transaction; capacity is freed. |
| B-09 | Max 2 active reservations per table per local evening, counting all sources (`online`, `phone`, `walk_in`); staff may override with `override_reason`. |
| B-10 | If both seating windows are used on one table, `second_start ≥ first_start + duration + buffer` (135 min) — automatically enforced by the protected intervals; applies regardless of booking order. |
| B-11 | Availability is computed independent of booking order; the allocator may reassign unlocked, not-yet-started reservations (F-18) before reporting a slot unavailable. |
| B-12 | Booking rules live in `BOOKING_RULES` (1:1 per restaurant) and are read dynamically; changing them requires no change to core reservation logic. Buffer changes grandfather existing allocations (`protected_until` computed at insert time). |
| B-13 | Booking horizon: dates from today to today + `booking_horizon_days` (30), in restaurant local time. |
| B-14 | All slot/seating math uses the restaurant's local timezone (`Europe/Copenhagen`); "evening" = local calendar date; timestamps stored as UTC `TIMESTAMPTZ`. |

## 8. Allocation & concurrency policy (summary of `restaurant_booking_policies.md`)

1. Begin transaction; `SELECT … FOR UPDATE` all affected table rows in **sorted order**.
2. Re-read affected reservations; validate seating rules, `is_locked`, capacity, enclave
   compatibility, duration, buffered availability.
3. Atomically update any reassigned (unlocked, future) allocations and insert the new
   reservation + allocations. Commit; on conflict roll back (existing reservations untouched).
4. PostgreSQL `EXCLUDE USING gist (table_id WITH =, tstzrange(protected_from, protected_until) WITH &&) WHERE (is_active)`
   on `RESERVATION_TABLE_ALLOCATIONS` is the hard DB-level guarantee (requires `btree_gist`).
5. Enclaves: `enclave_id NULL` = not joinable; same non-NULL enclave = joinable. Allocator
   preference order: (1) valid capacity/availability on every candidate table, (2) preserve useful
   table combinations, (3) minimize reassignment of existing reservations, (4) minimize unused
   seating capacity, (5) `allocation_priority` (lower = preferred) as tie-breaker. Availability
   queries may simulate reassignment plans but never apply them.
6. `is_locked` is writable only via staff endpoints (app-level enforcement). Locked and
   already-started reservations are never moved — automatically, and in the MVP also not manually.
   Reassigned reservations keep id, times, customer, and manage token. Customers are never notified
   of table changes (they never chose a table) and cannot alter allocations or `is_locked`.

## 9. Non-functional requirements

| ID | Requirement | Verification |
|---|---|---|
| NF-01 | Invalid reservations rejected | Automated tests |
| NF-02 | Consistency under concurrent requests | Integration + concurrency tests (AC-02) |
| NF-03 | Admin functions access-protected | Auth/authorization tests |
| NF-04 | Backend input validation | Tests with invalid input |
| NF-05 | Usable on mobile and desktop | Manual responsive testing |
| NF-06 | Documented startup/configuration | Installation test |
| NF-07 | Automated tests for core booking rules | Test results in CI |
| NF-08 | Customer PII handled responsibly: secrets in env vars only; PII minimized; 90-day anonymization job (§10); `manage_token` treated as secret | Review + job test |
| NF-09 | **Performance:** p95 < 1 s warm under k6 load: 50 virtual users, 5 minutes, availability lookups + booking attempts, test database, emails disabled. Cold starts (Render free tier, 30–60 s after 15 min idle) excluded and documented as MVP limitation | k6 run, documented |

## 10. Data protection & retention

After 90 days (single-transaction job, runnable/documented — not hand-run SQL):

1. `RESERVATIONS.customer_id = NULL` (FK `ON DELETE SET NULL`)
2. `RESERVATIONS.customer_note = NULL`
3. `RESERVATIONS.manage_token = NULL`
4. `RESERVATIONS.anonymized_at = CURRENT_TIMESTAMP`
5. Delete the associated `CUSTOMERS` row (each reservation has its own customer row)
6. Reservation row preserved for historical statistics; expired `TABLE_NOTES` deleted per policy

`CUSTOMERS.email` is **not unique**; email is contact info, not identity.

## 11. Data model (summary)

10 tables (see `database-diagram/ER-diagram.2.0.svg`): `RESTAURANTS`, `BOOKING_RULES` (1:1),
`OPENING_HOURS` (`open_time`, `kitchen_close_time`, `close_time`), `TABLE_ENCLAVES`,
`RESTAURANT_TABLES` (with `enclave_id`, `allocation_priority`),
`STAFF_USERS`, `CUSTOMERS`, `RESERVATIONS` (incl. `source`, `is_locked`, `customer_note`,
`override_reason`, `manage_token` UNIQUE NULL, `email_sent_at`, `anonymized_at`),
`RESERVATION_TABLE_ALLOCATIONS` (`protected_from`, `protected_until`,
`is_active`), `TABLE_NOTES`.

Key constraints: `UNIQUE(BOOKING_RULES.restaurant_id)`, `UNIQUE(RESTAURANT_TABLES(restaurant_id, table_number))`,
`UNIQUE(TABLE_ENCLAVES(restaurant_id, name))`, `UNIQUE(STAFF_USERS.email)`, `UNIQUE(RESERVATIONS.manage_token)` when populated;
`CHECK (party_size > 0)`, `CHECK (capacity > 0)`, `CHECK (ends_at > starts_at)`,
`CHECK (TABLE_NOTES.expires_at > created_at)` when present; `status ∈ {'active','cancelled'}`,
`source ∈ {'online','phone','walk_in'}`; online ⇒ `created_by_staff_id IS NULL AND manage_token IS NOT NULL`;
staff-created ⇒ `created_by_staff_id IS NOT NULL AND manage_token IS NULL`. All table/enclave IDs in an
allocation must belong to the reservation's restaurant.

### Seed dataset (MVP demo — idempotent seed script, separate from migrations)

- **Restaurant:** id 1, "Demo Restaurant", timezone `Europe/Copenhagen`, horizon 30 days
- **Enclaves:** 1 "Enclave 1" (combined capacity 6), 2 "Enclave 2" (combined capacity 4)
- **Tables:** #1 cap 4, enclave NULL, priority 40 · #2 cap 2, NULL, 10 · #3 cap 2, E1, 30 ·
  #4 cap 2, E1, 31 · #5 cap 2, E1, 32 · #6 cap 2, E2, 20 · #7 cap 2, E2, 21
- **Opening hours:** Monday closed (no row); Tue–Sun open 17:30, kitchen close 21:00, close 00:00 (next day)
- **Booking rules:** first seating 17:30–18:15, duration 120, buffer 15, slot interval 15,
  max online party size 6, max seatings per table 2, horizon 30 (second window derives to 19:45–20:30)
- **Staff:** `admin@demo-restaurant.example`, role `admin`, Argon2id hash of a password supplied
  via environment variable (never hardcoded)

## 12. Technology & architecture

```
FastAPI
 ├── API routes
 ├── Pydantic schemas        (request/response validation)
 ├── Services                (booking business logic: availability, allocation, concurrency)
 ├── SQLAlchemy 2.x models   (database entities)
 └── Alembic                 (migrations; `alembic upgrade head` as Render pre-deploy)

Frontend: Svelte SPA built with Vite → dist/ served by FastAPI (StaticFiles) on the same Render service
Database: PostgreSQL 16 on Neon, EU region Frankfurt (eu-central-1), sslmode=require, DATABASE_URL env var
```

- **SQLAlchemy 2.x + separate Pydantic schemas** (not SQLModel) — chosen for explicit control over
  complex relationships, transactions, and PostgreSQL-specific constraints.
- Auth: staff email+password, Argon2/bcrypt hash, HTTP-only signed cookie session (no JWT);
  staff scoped to their `restaurant_id`.
- Email: transactional provider (Resend recommended), API key in env vars only; sent after commit.
- Docker: multi-stage (Node builds Svelte `dist/`, `python:3.12-slim` runs uvicorn on `$PORT`).
- Local dev: `docker compose` (app + `postgres:16`); `.env` gitignored; `.env.example` committed.
- CI: GitHub Actions runs pytest on PRs / merges to `main`; `main` branch-protected (green PRs only).
- Deploy: merge to `main` → Render builds Docker image → pre-deploy `alembic upgrade head` →
  live at `https://<app>.onrender.com`. Free-tier cold start documented as MVP limitation.

The system project structure should look like this:
    booking-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── security/
│   │   ├── database/
│   │   └── main.py
│   ├── tests/
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
├── docs/
├── docker-compose.yml
└── README.md

Directory	Responsibility
api/	REST endpoints and controllers
config/	Application configuration
schemas/	DTOs and Pydantic validation models
models/	SQLAlchemy entities
repositories/	Database queries and persistence
services/	Business logic and business rules
security/	Authentication and authorization
database/	Database connections and sessions
tests/	Unit, integration and acceptance tests
migrations/	Database schema migrations


## 13. Test strategy

Unit (seating windows, slot grid, buffer, pair rule, allocation/enclave logic) · integration
(API + DB, migrations) · concurrency (competing bookings on same slot → one 409; EXCLUDE constraint) ·
e2e (customer booking flow, staff admin flow) · manual (responsive, error scenarios) ·
performance (k6 spec in NF-09) · retention job test (AC-07). Test cases derive from the ACs above.

## 14. MVP success criteria

- [ ] Customer completes a booking from the frontend; confirmation + email with cancel link work
- [ ] Reservation + allocations stored correctly; double bookings impossible (AC-02)
- [ ] Availability respects windows, opening hours, capacity, enclaves, horizon, order independence
- [ ] Staff can log in, view per date, create (incl. phone/walk-in), cancel, and move table allocations
- [ ] Config via seed data (tables, enclaves, hours, rules); backend reads it dynamically
- [ ] CI tests pass on `main`; app deployed and reachable via browser on Render
- [ ] 90-day anonymization job implemented and tested; install/config documented

## 15. Settled open questions (former PRD §14, all resolved)

1. Tables are auto-assigned (best-fit / enclave); customers never pick a table.
2. Settings (tables/hours/rules) configured via DB seed in MVP; no admin settings UI (F-12 deferred).
3. Customers can self-cancel via `manage_token` link (F-20, Must).
4. Reservations are immutable after creation **except table allocation**: staff may reassign tables
   in place (F-14), preserving id and token; date/time/party changes = cancel + rebook.
5. Parties > 6: directed to phone/email contact (B-02).
6. Backend: **FastAPI + SQLAlchemy 2.x** (supersedes the earlier SQLModel note) + Pydantic schemas + Alembic.
7. Deploy: FastAPI on Render (Docker, auto-deploy from `main`, pre-deploy `alembic upgrade head`),
   PostgreSQL on Neon Frankfurt; `DATABASE_URL` in `.env` locally and Render env settings.
8. Performance limits: NF-09 as specified above (k6, 50 VU, 5 min, warm p95 < 1 s).

## Appendix — cross-references

- Domain vocabulary: `GLOSSARY.md`; hard-to-reverse decisions: `docs/adr/0001`–`0012`
- Policy details and schema: `database-diagram/booking_policies.2.0.md`, `database-diagram/ER-diagram.2.0.svg`
  (the earlier `ER-diagram.png` / `restaurant_booking_policies*.md` are superseded)
- Naming: the ER column is `max_online_party_size` (an earlier note said `max_party_size` — ER name is canonical)
- Spec for implementation: `.scratch/restaurant-booking-mvp/spec.md`
