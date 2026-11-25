# Deployment: Render + Neon Frankfurt, CI-gated, Alembic pre-deploy

Status: accepted

The FastAPI app is packaged as a multi-stage Docker image (Node stage builds the Svelte/Vite SPA,
Python stage runs uvicorn on `$PORT`; the built `dist/` is served by FastAPI via StaticFiles on the
same service) and deployed as a Render web service with root directory `backend/`, auto-deploying
from the branch-protected `main` after a green pytest run in GitHub Actions. `alembic upgrade head`
runs as the Render pre-deploy command. PostgreSQL 16 runs on Neon in the EU region (Frankfurt,
eu-central-1) for GDPR residency, reached only via the `DATABASE_URL` env var (local `.env`
gitignored, prod value in Render's dashboard; `sslmode=require`). Demo seed data lives in an
idempotent seed script separate from schema migrations; the retention job has a manual + scheduled
runner. The Render free tier's cold start (30–60 s after 15 min idle) is accepted and documented
as an MVP limitation; NF-09 measures warm p95 < 1 s via k6 (50 VU, 5 min, test DB, emails disabled).
