# Docker Configuration

This directory contains Docker configuration files for the SEIM project.

## Files Overview

- **Dockerfile**: Main application container image
- **docker-compose.yml**: Development environment composition
- **.env.dev**: Development environment variables
- **restart_clean.bat**: Windows batch script for clean restart

## Containers

### Web Container (Django Application)
- **Base Image**: Python 3.9-slim
- **Port**: 8000
- **Volumes**: 
  - `/app`: Application code
  - `/media`: User uploads
- **Environment**: Development settings

### Database Container (PostgreSQL)
- **Image**: PostgreSQL 13
- **Port**: 5432
- **Volumes**: Persistent data storage
- **Credentials**: Configured in `.env` file

## Quick Start

### Development Environment

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Common Operations

```bash
# View logs
docker-compose logs web
docker-compose logs -f web  # Follow logs

# Execute commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web bash

# Run one-off commands
docker-compose run --rm web python manage.py test
docker-compose run --rm web pytest
```

## Environment Variables

Create a `.env` file in the project root with:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=seim
POSTGRES_USER=seim_user
POSTGRES_PASSWORD=seim_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis (if using)
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Docker Compose Services

### web
The main Django application service.

```yaml
web:
  build: .
  ports:
    - "8000:8000"
  volumes:
    - .:/app
    - media_volume:/app/media
  environment:
    - DJANGO_SETTINGS_MODULE=seim.settings
    - POSTGRES_HOST=db
  depends_on:
    - db
```

### db
PostgreSQL database service.

```yaml
db:
  image: postgres:13
  ports:
    - "5432:5432"
  environment:
    - POSTGRES_DB=seim
    - POSTGRES_USER=seim_user
    - POSTGRES_PASSWORD=seim_pass
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

## Production Configuration

For production deployment, use a separate `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=seim.settings.production
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    command: gunicorn seim.wsgi:application --bind 0.0.0.0:8000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/static
      - media_volume:/media
      - ssl_certs:/etc/nginx/ssl
    depends_on:
      - web
```

## Dockerfile Details

### Development Dockerfile
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media directory
RUN mkdir -p /app/media

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Production Dockerfile
```dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy supervisor config
COPY docker/supervisor.conf /etc/supervisor/conf.d/

# Expose port
EXPOSE 8000

# Start supervisor
CMD ["/usr/bin/supervisord"]
```

## Volumes

### Named Volumes
- `postgres_data`: PostgreSQL data persistence
- `media_volume`: User uploaded files
- `static_volume`: Static files (production)

### Bind Mounts
- `./app`: Application code (development)

## Networking

Docker Compose creates a default network for all services. Services can communicate using their service names as hostnames.

Example:
- Web app connects to database using `db:5432`
- Nginx proxies to web app using `web:8000`

## Health Checks

Add health checks to ensure services are running properly:

```yaml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U seim_user"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Rebuild image
docker-compose build --no-cache web

# Check Dockerfile syntax
docker build -t test .
```

### Permission issues
```bash
# Fix ownership
docker-compose exec web chown -R www-data:www-data /app/media

# Check permissions
docker-compose exec web ls -la /app/
```

### Database connection issues
```bash
# Check if database is ready
docker-compose exec db pg_isready

# Check environment variables
docker-compose exec web printenv | grep POSTGRES

# Test connection
docker-compose exec web python manage.py dbshell
```

### Port conflicts
```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
# Modify docker-compose.yml:
ports:
  - "8001:8000"
```

## Best Practices

1. **Use specific image versions**
   ```yaml
   image: postgres:13.3
   ```

2. **Set resource limits**
   ```yaml
   services:
     web:
       deploy:
         resources:
           limits:
             cpus: '0.50'
             memory: 512M
   ```

3. **Use secrets for sensitive data**
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

4. **Multi-stage builds for smaller images**
   ```dockerfile
   # Build stage
   FROM python:3.9 as builder
   COPY requirements.txt .
   RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

   # Final stage
   FROM python:3.9-slim
   COPY --from=builder /wheels /wheels
   RUN pip install --no-cache /wheels/*
   ```

5. **Use .dockerignore**
   ```
   **/__pycache__
   **/*.pyc
   .git
   .env
   media/*
   static/*
   ```

## Security Considerations

1. **Don't run as root**
   ```dockerfile
   RUN useradd -m myuser
   USER myuser
   ```

2. **Scan for vulnerabilities**
   ```bash
   docker scan seim:latest
   ```

3. **Use secure environment variables**
   ```yaml
   environment:
     - DJANGO_SECRET_KEY_FILE=/run/secrets/django_secret
   ```

4. **Network isolation**
   ```yaml
   networks:
     frontend:
     backend:
       internal: true
   ```

## Maintenance

### Cleanup
```bash
# Remove unused images
docker image prune

# Remove all unused objects
docker system prune -a

# Remove specific containers
docker-compose rm web
```

### Backup
```bash
# Backup database
docker-compose exec db pg_dump -U seim_user seim > backup.sql

# Backup volumes
docker run --rm -v seim_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup.tar.gz /data
```

### Updates
```bash
# Update base images
docker-compose pull

# Rebuild with new requirements
docker-compose build --no-cache

# Update specific service
docker-compose up -d --no-deps --build web
```

## Performance Optimization

1. **Build caching**
   ```dockerfile
   # Copy requirements first for better caching
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   ```

2. **Layer optimization**
   ```dockerfile
   # Combine RUN commands
   RUN apt-get update \
       && apt-get install -y package1 package2 \
       && rm -rf /var/lib/apt/lists/*
   ```

3. **Use Alpine images when possible**
   ```dockerfile
   FROM python:3.9-alpine
   ```

This Docker configuration provides a complete development and production setup for the SEIM project. Always test changes locally before deploying to production.
