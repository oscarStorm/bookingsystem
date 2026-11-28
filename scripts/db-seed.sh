#!/usr/bin/env bash
# Apply migrations and run the idempotent demo seed against the local dev
# database. Reads .env at the repo root if present. The admin password must
# come from SEED_ADMIN_PASSWORD (env or .env) — it is never hardcoded.
# Usage: scripts/db-seed.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/db-common.sh"

if [ ! -x "$ROOT/backend/.venv/bin/python" ]; then
  echo "Creating backend virtualenv..."
  python3 -m venv "$ROOT/backend/.venv"
fi
"$ROOT/backend/.venv/bin/pip" install -q -r "$ROOT/backend/requirements.txt"

if [ -f "$ROOT/.env" ]; then set -a; . "$ROOT/.env"; set +a; fi
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://$PG_USER@localhost:$PG_PORT/$PG_DB}"
export SECRET_KEY="${SECRET_KEY:-dev-only-not-a-secret}"
if [ -z "${SEED_ADMIN_PASSWORD:-}" ]; then
  echo "warning: SEED_ADMIN_PASSWORD is not set; the seed will fail to create the admin staff user." >&2
fi

cd "$ROOT/backend"
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed
