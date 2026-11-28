#!/usr/bin/env bash
# Start the local development PostgreSQL server (pg_ctl), create the app
# database if missing, and apply Alembic migrations when the backend venv
# exists. Usage: scripts/db-start.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/db-common.sh"

[ -x "$PG_BIN/postgres" ] || install_postgres
mkdir -p "$PG_RUN"

if "$PG_BIN/pg_ctl" -D "$PG_DATA" status >/dev/null 2>&1; then
  echo "PostgreSQL is already running (port $PG_PORT)."
else
  if [ ! -f "$PG_DATA/PG_VERSION" ]; then
    "$PG_BIN/initdb" -D "$PG_DATA" -U "$PG_USER" --auth=trust -E UTF8 >/dev/null
  fi
  "$PG_BIN/pg_ctl" -D "$PG_DATA" -o "-p $PG_PORT -k $PG_RUN" -l "$PG_HOME/postgres.log" -w start
  echo "PostgreSQL started on port $PG_PORT (data dir: $PG_DATA)."
fi

if ! "$PG_BIN/psql" -h localhost -p "$PG_PORT" -U "$PG_USER" -d postgres -tc \
     "SELECT 1 FROM pg_database WHERE datname = '$PG_DB'" | grep -q 1; then
  "$PG_BIN/psql" -h localhost -p "$PG_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $PG_DB" >/dev/null
  echo "Created database '$PG_DB'."
fi

if [ -x "$ROOT/backend/.venv/bin/alembic" ]; then
  if [ -f "$ROOT/.env" ]; then set -a; . "$ROOT/.env"; set +a; fi
  export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://$PG_USER@localhost:$PG_PORT/$PG_DB}"
  export SECRET_KEY="${SECRET_KEY:-dev-only-not-a-secret}"
  ( cd "$ROOT/backend" && .venv/bin/alembic upgrade head )
fi

echo
echo "Browse from your terminal:"
echo "  psql -h localhost -U $PG_USER -d $PG_DB"
echo "  scripts/db-psql.sh            # bundled psql wrapper"
echo "Seed demo data:  scripts/db-seed.sh    Stop: scripts/db-stop.sh"
