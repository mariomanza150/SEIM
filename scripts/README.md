# Scripts Directory

This directory contains various scripts used for running and managing the SEIM Django application.

## Scripts

### entrypoint.sh
The main production entrypoint script that:
- Creates necessary directories with proper permissions
- Runs database migrations
- Collects static files
- Creates a default superuser (if not exists)
- Starts Gunicorn with production settings

### entrypoint-dev.sh
Development-specific entrypoint script that:
- Waits for PostgreSQL to be ready
- Runs migrations and collects static files
- Creates a development superuser
- Starts Gunicorn with reload enabled or Django development server

### entrypoint-flexible.sh
A more configurable entrypoint script that:
- Supports environment variables for customization
- Can skip DB operations with SKIP_DB_WAIT=true
- Conditionally creates superuser based on CREATE_SUPERUSER=true
- Automatically switches between dev and production modes based on DJANGO_ENV
- Allows customization of Gunicorn settings via environment variables

### healthcheck.sh
Simple health check script for Docker health checks.

## Usage

### In Docker
The scripts are automatically copied into the Docker container and used as entrypoints.

### Environment Variables for flexible entrypoint

- `DJANGO_ENV`: Set to "dev" or "development" for development mode
- `SKIP_DB_WAIT`: Set to "true" to skip waiting for database
- `CREATE_SUPERUSER`: Set to "true" to create a superuser on startup
- `SUPERUSER_USERNAME`: Username for the superuser (default: admin)
- `SUPERUSER_EMAIL`: Email for the superuser (default: admin@example.com)
- `SUPERUSER_PASSWORD`: Password for the superuser (default: admin123)
- `GUNICORN_WORKERS`: Number of Gunicorn workers (default: 4)
- `GUNICORN_THREADS`: Number of threads per worker (default: 2)
- `GUNICORN_TIMEOUT`: Request timeout in seconds (default: 30)
- `GUNICORN_LOG_LEVEL`: Log level (default: info)

### Direct Usage
Make sure to set execute permissions:
```bash
chmod +x scripts/*.sh
```

Then run:
```bash
./scripts/entrypoint.sh
```
