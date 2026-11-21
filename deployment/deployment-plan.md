# Deployment Plan & Learning Roadmap — Restaurant Booking System

This document is the plan for **what to understand and do** to reach the deployment setup
decided in `PRD.md` §14.7 (with Docker added per §11 "containerbaseret idriftsættelse"):

```
git push / PR → merge to main → GitHub Actions runs pytest → Render builds Docker image
    → pre-deploy: alembic upgrade head → new container live at https://<app>.onrender.com
    → app connects to Neon PostgreSQL via DATABASE_URL (secret env var)
```

| Component | Technology | Hosted where | Config |
|---|---|---|---|
| Backend API | FastAPI + SQLModel, packaged as Docker image | Render (web service, Docker environment, auto-deploy from `main`) | `DATABASE_URL` in Render env settings; `.env` locally |
| Database | PostgreSQL 16 (schema per `database-diagram.md`) | Neon, **EU region (Frankfurt, eu-central-1)** | `DATABASE_URL` connection string |
| Migrations | Alembic | Run as Render pre-deploy command | `alembic upgrade head` |
| CI gate | GitHub Actions (pytest) | GitHub, on PRs / merges to `main` | `.github/workflows/tests.yml` |
| Frontend (MVP) | Static files served by FastAPI (`StaticFiles`) — alternative: separate static host (Vercel/Netlify/Cloudflare Pages) | Same Render service (MVP) or separate | `API_BASE_URL` if split |
| Secrets | Never in Git | Local: `.env` (gitignored) / Prod: Render dashboard "Environment" | `.env.example` committed as template |

---

## 1. Learning path (in order)

Work through these in sequence. Each has: **what to understand → why it matters here → hands-on milestone → done when**.

### 1. Git & GitHub workflow — the deploy trigger
- **Understand:** branches, pull requests, merge to `main`, branch protection rules, required status checks.
- **Why:** "merge to main = deploy" only works if `main` is protected and every merge is tested first.
- **Milestone:** create a PR, merge it, confirm nothing breaks; enable branch protection on `main` requiring the CI check (added in step 7).
- **Done when:** you can explain why direct pushes to `main` should be blocked.

### 2. Environment variables & secrets
- **Understand:** what env vars are; `.env` files; `.gitignore`; `python-dotenv` for loading `.env` locally; why secrets must never be committed; the `DATABASE_URL` connection-string format (`postgresql://user:pass@host/db?sslmode=require`).
- **Why:** the same code must run locally (local `.env`) and on Render (dashboard env vars) without code changes — this is the core of the §14.7 decision.
- **Milestone:** app reads `DATABASE_URL` from env; add `.env` to `.gitignore`; commit only `.env.example` with placeholder values.
- **Done when:** `git status` never shows `.env`, and the app starts locally using `.env`.

### 3. Docker — packaging the FastAPI app
- **Understand:** image vs container; writing a `Dockerfile` (multi-stage `python:3.12-slim`, `pip install -r requirements.txt`, `COPY app`, `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`); `.dockerignore`; why `$PORT` must come from the environment (Render injects it); `docker compose` for local dev (FastAPI container + `postgres:16` container) so local mirrors prod.
- **Why:** §11 asks for a reproducible, containerized deployment; Docker makes local = production and is what Render's "Docker" environment runs.
- **Milestone:** `docker compose up` locally → API answers on `localhost:8000` against a local Postgres container.
- **Done when:** you can rebuild the image from scratch and the app still works; `.env` is not baked into the image.

### 4. Neon — the PostgreSQL database
- **Understand:** creating a Neon project; choosing the **EU region (Frankfurt)** — relevant for GDPR/NF-08 since customer names, emails and phone numbers are stored; copying the connection string into `DATABASE_URL` (`sslmode=require`); Neon dev branches (one branch per PR / local dev DB); how to run SQL in the Neon console (needed for `CREATE EXTENSION btree_gist;` and the exclusion constraint from `database-diagram.md`).
- **Why:** the DB is a separate, persistent service — it survives app redeploys and is never exposed publicly; only the app connects via the secret connection string.
- **Milestone:** connect from local FastAPI (via `.env`) and insert/select a row in `psql` or the Neon SQL editor.
- **Done when:** `DATABASE_URL` works from both your laptop and (later) Render.

### 5. SQLModel + Alembic — schema & migrations
- **Understand:** mapping the 7 ER tables (`restaurants`, `booking_rules`, `opening_hours`, `restaurant_tables`, `customers`, `reservations`, `staff_users`) to SQLModel classes; `alembic init`, `alembic revision --autogenerate`, `alembic upgrade head`; why migrations must run **on deploy** (Render pre-deploy command), never by hand-editing the DB; enabling `btree_gist` on Neon for the no-overlap exclusion constraint (AC-02).
- **Why:** the PRD note in §14 asks for "a fixed way to run database migrations, e.g. Alembic" — this is it.
- **Milestone:** generate the initial migration from the models, run it against a Neon dev branch, verify tables exist.
- **Done when:** `alembic upgrade head` creates the full schema from an empty database.

### 6. Render — hosting the container
- **Understand:** PaaS concept (you don't manage servers); creating a **Web Service** with **Environment: Docker** pointed at your `Dockerfile`; auto-deploy ON with `main` as deploy branch; setting env vars (`DATABASE_URL`) in the dashboard; **Pre-Deploy Command** = `alembic upgrade head`; reading build/deploy **logs**; the free-tier caveat (sleeps after 15 min idle → ~30–60 s cold start; paid instance stays warm); optionally `render.yaml` in the repo to define the service as code.
- **Why:** this is the §14.7 decision: FastAPI on Render, HTTPS URL automatic, merge-to-main deploys.
- **Milestone:** first deploy of a hello-world FastAPI container → live at `https://<app>.onrender.com` → merge a PR changing a string → watch auto-deploy in the logs.
- **Done when:** the API is reachable over HTTPS and every merge to `main` produces a new live version.

### 7. CI — tests before merge
- **Understand:** GitHub Actions workflow (`.github/workflows/tests.yml`) that runs `pytest` on every PR and push to `main`; combining with branch protection so `main` requires green tests; test layers from PRD §12 (unit: booking rules B-01–B-12; integration: API + DB; concurrency tests for AC-02).
- **Why:** the §14 note: "add automated tests before merge" — broken code should never reach Render.
- **Milestone:** a failing test blocks a merge; a passing PR merges and auto-deploys.
- **Done when:** `main` is protected and only mergeable via green PRs.

### 8. FastAPI in production
- **Understand:** production start command (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`); a `/health` endpoint for Render health checks; CORS config (needed if frontend is hosted separately); serving the built frontend via `StaticFiles` for the MVP; `API_BASE_URL` env var for the frontend if split later.
- **Why:** Render kills/restarts containers, so the app must be stateless and bind to the injected port.
- **Milestone:** `/health` returns 200 on the Render URL; booking flow works end-to-end through the deployed API.
- **Done when:** a reservation created via the browser is visible in the Neon database.

### 9. Security & GDPR basics
- **Understand:** secrets only via env vars; `password_hash` (Argon2/bcrypt) never plaintext; the `manage_token` UUID for self-service cancellation (§14.3); HTTPS everywhere (Render provides it; Neon requires `sslmode=require`); EU data residency (Neon Frankfurt region) and a DPA with the hosting provider; `.env` never in Git (NF-08).
- **Why:** customer personal data is stored; NF-03/NF-08 require protected admin and responsible data handling.
- **Milestone:** `.env` absent from `git log`; admin endpoints require auth in the deployed app.
- **Done when:** you can list where each secret lives and who can access it.

### 10. Observability & operations
- **Understand:** reading Render deploy/runtime logs; Neon dashboard (connections, storage, compute); basic alerting/uptime check; how to roll back on Render (redeploy previous commit).
- **Why:** PRD §13 requires the app to be deployable and documented; you need to debug production issues.
- **Milestone:** intentionally break something on a branch, see the deploy fail in logs, roll back.
- **Done when:** you can find the last 100 log lines of the live service in under a minute.

---

## 2. Suggested build order (milestones)

1. FastAPI skeleton with `/health` running locally with `uvicorn`.
2. Add `.env` + `.gitignore` + `.env.example`; load `DATABASE_URL` via dotenv.
3. SQLModel models for the 7 ER tables + Alembic; run migrations against local Postgres in `docker compose`.
4. `Dockerfile` + `.dockerignore`; app runs in a container locally (`docker compose up`).
5. Push repo to GitHub; protect `main`; add GitHub Actions pytest workflow.
6. Create Neon project (Frankfurt region); put its `DATABASE_URL` in `.env`; run `alembic upgrade head`.
7. Create Render web service (Docker env, auto-deploy from `main`, env var `DATABASE_URL`, pre-deploy `alembic upgrade head`) → live HTTPS URL.
8. Merge a PR end-to-end: tests pass → Render deploys → verify data lands in Neon.
9. Add `render.yaml`, frontend serving decision, and write the deployment section of the report (install/config documentation, PRD §13).

## 3. Files this plan will produce in this repo

```
├── Dockerfile                  # multi-stage FastAPI image, uvicorn on $PORT
├── .dockerignore               # .env, __pycache__, .git, etc.
├── docker-compose.yml          # local dev: app + postgres:16
├── .env                        # LOCAL ONLY (gitignored) — DATABASE_URL=postgresql://...localhost...
├── .env.example                # committed template with placeholders
├── render.yaml                 # Render service as code (optional but recommended)
├── alembic.ini + alembic/      # migrations; pre-deploy runs `alembic upgrade head`
└── .github/workflows/tests.yml # pytest on PRs / merges to main
```

## 4. Verification checklist (maps to PRD §13 success criteria)

- [ ] App reachable via browser at the HTTPS URL (Render).
- [ ] Every merge to `main` auto-deploys (watch Render events log).
- [ ] Migrations run automatically on deploy; schema in Neon matches `database-diagram.md` (incl. `btree_gist` exclusion constraint).
- [ ] `DATABASE_URL` works locally from `.env` and in prod from Render env vars; `.env` never committed.
- [ ] `pytest` runs in CI before merge; `main` is branch-protected.
- [ ] A reservation created in the UI is visible in Neon.
- [ ] Free-tier cold start understood and documented (paid instance if fast responses are needed all day).
- [ ] Install/config steps documented (this file + README) — PRD §13 last item.

## 5. Resources

- Render: "Deploy a FastAPI app" / Docker deployment guide, env vars guide, free-tier cold-start docs, `render.yaml` reference → render.com/docs
- Neon: quickstart, connection string / `sslmode=require`, database branching, EU regions → neon.tech/docs
- Alembic + SQLModel: Alembic tutorial, SQLModel docs (FastAPI integration) → sqlmodel.tiangolo.com, alembic.sqlalchemy.org
- Docker: Dockerfile reference, docker compose docs → docs.docker.com
- GitHub Actions: "Python CI with pytest", branch protection docs → docs.github.com
- GDPR angle for a Danish system: EU region choice on Neon; DPA requirements (Datatilsynet guidance)
