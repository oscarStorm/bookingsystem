#!/usr/bin/env bash
# Open psql against the local dev database using the bundled PostgreSQL client.
# Usage: scripts/db-psql.sh [-d otherdb] [-- any psql args]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/db-common.sh"
exec "$PG_BIN/psql" -h localhost -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" "$@"
