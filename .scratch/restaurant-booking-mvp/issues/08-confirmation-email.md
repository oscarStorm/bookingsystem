# 08: Confirmation email

**What to build:** Exactly one confirmation email per online reservation, sent after the database commit via Resend (API key from env vars only — never in git, per ADR-0008), containing the reservation details and the cancellation link, with no allergy or other sensitive note content. `email_sent_at` records provider acceptance for idempotent resend protection; email failure never blocks or invalidates the booking; the on-screen confirmation always shows the cancellation link regardless of email outcome.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] After a successful online booking, one email is sent post-commit and email_sent_at is set; a resend attempt is a no-op
- [ ] Simulated email failure: booking still returns 201 and the link is still shown on screen
- [ ] Email body contains reservation details + manage link and no customer-note content
