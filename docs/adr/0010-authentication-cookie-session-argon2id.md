# Staff authentication: Argon2id + HTTP-only cookie session, no JWT

Status: accepted

Staff log in with email + password; passwords are stored as Argon2id hashes (never plaintext).
The admin UI is served from the same origin as the API, so authentication uses an HTTP-only signed
cookie session (Starlette SessionMiddleware) rather than JWT — no token to leak via XSS, and no
refresh-token machinery needed for the MVP. One role in the MVP; staff are scoped to their
`restaurant_id`, and the `is_locked` flag is writable only through staff endpoints (enforced at the
application level, since PostgreSQL CHECKs cannot see roles).
