#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."

# Function to check if database is ready
check_db() {
    python manage.py check --database default 2>&1 | grep -q "System check identified no issues"
}

# Wait for database with timeout
timeout=60
counter=0
while ! check_db && [ $counter -lt $timeout ]; do
    echo "Database not ready yet... waiting ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "ERROR: Database connection timeout after ${timeout} seconds"
    exit 1
fi

echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup complete!" 