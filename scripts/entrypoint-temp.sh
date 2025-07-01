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
    
    # Create migrations for any changes
    echo "Creating any needed migrations..."
    python manage.py makemigrations --noinput || true
    
    # Apply any new migrations
    echo "Applying new migrations..."
    python manage.py migrate --noinput
fi

# Try to collect static files, skip if it fails for now
echo "Attempting to collect static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

# Setup initial data (includes admin user creation with proper checks)
echo "Setting up initial data..."
python manage.py setup_initial_data || echo "Initial data setup failed, continuing..."

# Start the application
echo "Starting application..."
exec python manage.py runserver 0.0.0.0:8000
