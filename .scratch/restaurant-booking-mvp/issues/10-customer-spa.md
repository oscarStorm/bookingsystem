# 10: Customer-facing SPA

**What to build:** The Svelte (Vite) customer booking UI served by the backend: date picker limited to the booking horizon, party size input (larger parties are told to contact the restaurant by phone/email), live slot list from the availability API, a details form (name, email, phone, optional note) with inline validation errors, an on-screen confirmation showing date, time, party size, and the cancellation link, and the self-cancel page reached via the manage_token link. Closed days show no availability; a 409 response shows alternative slots.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] E2E: pick date → party size → slot → details → confirmation with cancellation link → cancel via the link
- [ ] Closed day shows no slots; party above the max online size shows the contact-the-restaurant message; invalid input shows field-level errors; 409 shows alternative slots
