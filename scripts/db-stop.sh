#!/usr/bin/env bash
# Stop the local development PostgreSQL server. Usage: scripts/db-stop.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/db-common.sh"

if [ ! -f "$PG_DATA/PG_VERSION" ]; then
  echo "No database initialized at $PG_DATA — nothing to stop."
  exit 0
fi
"$PG_BIN/pg_ctl" -D "$PG_DATA" -m fast stop
