#!/bin/bash
set -e

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL..."
    while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER:-seim_user}" -d "${POSTGRES_DB:-seim}" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is ready!"
}

# Create necessary directories
echo "Creating directories..."
mkdir -p /app/media/exchanges /app/logs /app/staticfiles
chmod -R 755 /app/media /app/logs /app/staticfiles

# Wait for database if not in standalone mode
if [ "$SKIP_DB_WAIT" != "true" ]; then
    wait_for_postgres
    
    # Run database migrations
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Setup initial data (includes admin user creation with proper checks)
echo "Setting up initial data..."
python manage.py setup_initial_data

# Start the application based on environment
echo "Starting application..."
if [ "$DJANGO_ENV" = "dev" ] || [ "$DJANGO_ENV" = "development" ]; then
    # Development mode with auto-reload
    exec gunicorn seim.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --threads 2 \
        --reload \
        --access-logfile - \
        --error-logfile - \
        --log-level debug \
        "$@"
else
    # Production mode
    exec gunicorn seim.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --threads ${GUNICORN_THREADS:-2} \
        --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
        --worker-connections ${GUNICORN_WORKER_CONNECTIONS:-1000} \
        --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
        --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
        --timeout ${GUNICORN_TIMEOUT:-30} \
        --access-logfile - \
        --error-logfile - \
        --log-level ${GUNICORN_LOG_LEVEL:-info} \
        "$@"
fi
