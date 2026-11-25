#!/usr/bin/env bash
# Entry for docker-compose.local-prod.yml web service: wait for Postgres, then gunicorn.
# Migrations run via the one-shot ``migrate`` Compose service (deploy script) before
# rollout. Static files are baked into the image at build time (no runtime collectstatic).
set -eu

echo "Waiting for database (DNS + TCP)..."
python /app/scripts/wait_for_db_tcp.py

echo "Starting Gunicorn..."
exec gunicorn seim.wsgi:application --bind 0.0.0.0:8000 --workers 2 --worker-class sync --timeout 30 --access-logfile - --error-logfile - --log-level info
