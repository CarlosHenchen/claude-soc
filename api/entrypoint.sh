#!/bin/sh
set -e

# --- Aviso (não-fatal) sobre segredos fracos -------------------------------
case "${SECRET_KEY:-}" in
  ""|dev-insecure-secret-change-me|change-me*)
    echo "[entrypoint] AVISO: SECRET_KEY fraco/padrão. Rode ./scripts/setup-env.sh ou gere com 'openssl rand -hex 32' antes de usar em produção." ;;
esac
if [ "${ADMIN_PASSWORD:-admin}" = "admin" ]; then
  echo "[entrypoint] AVISO: ADMIN_PASSWORD ainda é 'admin' — troque assim que possível."
fi

echo "[entrypoint] Running database migrations..."
alembic upgrade head

if [ "${AUTO_SEED:-1}" = "1" ]; then
  echo "[entrypoint] Seeding catalog from spreadsheet..."
  python -m app.cli seed || echo "[entrypoint] seed skipped/failed (continuing)"
fi

echo "[entrypoint] Starting Uvicorn (${UVICORN_WORKERS:-1} worker(s))..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-1}"
