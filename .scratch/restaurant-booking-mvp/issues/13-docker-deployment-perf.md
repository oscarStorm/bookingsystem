# 13: Docker image, deployment wiring, and performance test

**What to build:** A multi-stage Dockerfile that builds the Svelte SPA in a Node stage and serves the built `dist/` via FastAPI StaticFiles on the same service; Render service wiring (env vars for DATABASE_URL, Resend key, session secret; pre-deploy `alembic upgrade head` before the new version goes live); a k6 performance test (50 virtual users, 5 minutes, mixed availability lookups and booking attempts against a test database, emails disabled) asserting warm p95 < 1 s, with documented run instructions; and branch protection on `main` requiring green PRs.

**Blocked by:** 10, 11.

**Status:** ready-for-agent

- [ ] The Docker image builds and serves both the API and the SPA; the pre-deploy migration runs before the new version goes live
- [ ] The k6 script runs locally against a test database and reports warm p95 < 1 s
- [ ] CI is green on `main` with branch protection requiring green PRs
