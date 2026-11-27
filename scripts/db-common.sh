#!/usr/bin/env bash
# Shared paths/config for the local dev-database scripts. Sourced, not executed.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PG_HOME="$ROOT/.pg"                 # gitignored; user-space PostgreSQL 16 lives here
PG_BIN="$PG_HOME/pginstall/bin"
PG_LIBS="$PG_HOME/pgserver.libs"
PG_DATA="$PG_HOME/data"
PG_RUN="$PG_HOME/run"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-bookingsystem}"
export LD_LIBRARY_PATH="$PG_LIBS${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# One-time install of a user-space PostgreSQL 16 (pgserver wheel) plus the
# btree_gist contrib module built from the matching source tarball.
install_postgres() {
  echo "Installing user-space PostgreSQL 16 into $PG_HOME (one-time download)..."
  command -v curl >/dev/null || { echo "error: curl is required" >&2; exit 1; }
  command -v python3 >/dev/null || { echo "error: python3 is required" >&2; exit 1; }
  local src="$PG_HOME/src"
  mkdir -p "$src"
  cd "$src"
  curl -sSL -o pg16.tar.gz https://ftp.postgresql.org/pub/source/v16.2/postgresql-16.2.tar.gz
  python3 -m pip download --no-deps --only-binary :all: --python-version 3.12 -d . pgserver
  unzip -q -o pgserver-*.whl -d pkg
  cp -r pkg/pgserver/pginstall "$PG_HOME/pginstall"
  cp -r pkg/pgserver.libs "$PG_HOME/pgserver.libs"
  tar xzf pg16.tar.gz postgresql-16.2/contrib/btree_gist
  ( cd postgresql-16.2/contrib/btree_gist \
      && PATH="$PG_BIN:$PATH" make -s USE_PGXS=1 \
      && PATH="$PG_BIN:$PATH" make -s USE_PGXS=1 install )
  echo "Installed: $("$PG_BIN/postgres" --version)"
}
