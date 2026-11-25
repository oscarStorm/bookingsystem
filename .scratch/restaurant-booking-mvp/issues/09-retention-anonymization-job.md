# 09: Retention anonymization job

**What to build:** A separately runnable cleanup script backed by a retention service (ADR-0009): 90 days after cancellation — or 90 days after the reservation date for completed/stale reservations — in a single transaction null the customer reference, customer note, and manage_token, set anonymized_at, and delete the dedicated customer row; also delete expired table notes. Reservation rows are preserved for future statistics.

**Blocked by:** 07.

**Status:** ready-for-agent

- [ ] Fixture reservations 91 days past cancellation/date: the job nulls the PII fields, stamps anonymized_at, and deletes the customer row in one transaction; reservation rows remain
- [ ] Reservations within 90 days are untouched; expired table notes are deleted, unexpired notes kept
- [ ] The script is runnable standalone (e.g. as a cron job or Render scheduled job)
