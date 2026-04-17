#!/usr/bin/env bash
# Entry for docker-compose.local-prod.yml web service: wait for Postgres, migrate, static, gunicorn.
set -eu

echo "Waiting for database (DNS + TCP)..."
python /app/scripts/wait_for_db_tcp.py

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn seim.wsgi:application --bind 0.0.0.0:8000 --workers 2 --worker-class sync --timeout 30 --access-logfile - --error-logfile - --log-level info
