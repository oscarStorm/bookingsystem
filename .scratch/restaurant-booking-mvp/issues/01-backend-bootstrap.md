# 01: Backend bootstrap — app skeleton, config, health, CI

**What to build:** A runnable FastAPI backend skeleton with the layered layout (api / config / schemas / models / repositories / services / security / database), environment-based configuration (`.env` gitignored, `.env.example` committed; DATABASE_URL, session secret, Resend API key, and the seed admin password come only from env vars — never from git), the database engine and session factory, a `GET /health` endpoint returning 200, pytest infrastructure, and a GitHub Actions workflow running pytest on every PR. No domain logic yet — the deliverable is that the service starts and CI is green.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Service starts locally with env-based config and `GET /health` returns 200
- [x] `.env` is gitignored; `.env.example` documents every required env var; no secrets anywhere in git
- [x] pytest runs (suite green) and the GHA workflow executes on PRs

## Comments

Implemented in the commit "Add FastAPI backend bootstrap (ticket 01)": layered `backend/app/` skeleton, pydantic-settings config reading only env vars (fail-fast on missing `DATABASE_URL`/`SECRET_KEY`), lazy SQLAlchemy engine + session factory, `GET /health`, pytest suite (8 tests: health HTTP seam, config seam, git-hygiene seam), mypy, `.gitignore`/`.env.example`, and `.github/workflows/tests.yml` (pytest on PRs + pushes to main, postgres:16 service, plain `pytest` with `pythonpath = .` in pytest.ini so collection works in CI).
