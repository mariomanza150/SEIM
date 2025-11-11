#!/bin/bash

# Reset Exchange App Migrations Script
# This script resets the exchange app migrations after removing DynamicForm

echo "🔄 Resetting Exchange App Migrations..."

# Stop containers
echo "📦 Stopping containers..."
docker-compose down

# Remove the database volume to start fresh
echo "🗄️ Removing database volume..."
docker volume rm seim_postgres_data 2>/dev/null || echo "Database volume not found or already removed"

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "📋 Running migrations..."
docker-compose exec web python manage.py migrate

# Create initial data
echo "📊 Creating initial data..."
docker-compose exec web python manage.py create_initial_data

# Check if everything is working
echo "✅ Checking application status..."
docker-compose exec web python manage.py check

echo "🎉 Exchange app migrations reset complete!"
echo "🌐 Application should be available at: http://localhost:8000"
echo "🔧 Admin interface at: http://localhost:8000/admin/"
echo "📝 Form builder at: http://localhost:8000/dynforms/" 