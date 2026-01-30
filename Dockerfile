# syntax=docker/dockerfile:1

# =============================================================================
# STAGE 1: Build Vue.js Frontend
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend-vue

# Copy package files
COPY frontend-vue/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend-vue/ ./

# Build Vue.js for production
RUN npm run build

# =============================================================================
# STAGE 2: Python/Django Application
# =============================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libmagic1 \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Note: Selenium tests run from HOST OS, not Docker containers
# Chrome and ChromeDriver are not installed in Docker

# Install Python dependencies
COPY requirements*.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# Copy project files
COPY . .

# Copy Vue.js build from frontend-builder stage
COPY --from=frontend-builder /app/frontend-vue/dist /app/frontend-vue/dist

# Create media directory for Wagtail uploads
RUN mkdir -p /app/media

# Collect static files (includes Vue.js assets)
RUN python manage.py collectstatic --noinput --clear

# Make the wait-for-db script executable
RUN chmod +x /app/scripts/wait-for-db.sh

# Expose port for Django
EXPOSE 8000

# Entrypoint for Django (can be overridden in docker-compose)
CMD ["/app/scripts/wait-for-db.sh"]
