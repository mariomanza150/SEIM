# syntax=docker/dockerfile:1
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

# Create media directory for Wagtail uploads
RUN mkdir -p /app/media

# Make the wait-for-db script executable
RUN chmod +x /app/scripts/wait-for-db.sh

# Expose port for Django
EXPOSE 8000

# Entrypoint for Django (can be overridden in docker-compose)
CMD ["/app/scripts/wait-for-db.sh"] 