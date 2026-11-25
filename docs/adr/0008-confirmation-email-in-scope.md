# Confirmation email is in scope (supersedes the original out-of-scope note)

Status: accepted

The MVP sends exactly one confirmation email per successful online reservation, via Resend (API
key in env vars, never in Git), containing the reservation details and the manage-token
cancellation link. The email is sent only after the database transaction commits; `email_sent_at`
records provider acceptance so retries never send twice. Email delivery failure never blocks or
invalidates the booking — the on-screen confirmation always shows the cancellation link. This
supersedes the original PRD §3.2, which listed email notifications as out of scope: only the
confirmation email is in; reminders, cancellation notifications, and reassignment notices remain
out of scope. The manage token is treated as a secret, and sensitive customer notes are never
included in emails.
