# Retention: 90-day anonymization job

Status: accepted

A scheduled job (also manually runnable) processes reservations 90 days after cancellation, or 90
days after the reservation date for completed/stale ones. For each due reservation, in a single
transaction: clear `customer_note` and `manage_token`, set the customer reference to NULL (FK
`ON DELETE SET NULL`), stamp `anonymized_at`, and delete the reservation's dedicated customer row.
The reservation row itself is preserved for historical statistics; expired table notes are deleted
automatically. This is the concrete implementation of NF-08 (GDPR); the Neon database runs in the
EU (Frankfurt) for data residency. Check constraints must permit NULL customer/token after
anonymization.
