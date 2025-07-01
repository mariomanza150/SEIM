<!--
File: docs/DEPLOYMENT.md
Title: Deployment Guide
Purpose: Explain how to deploy the SEIM system to production, including prerequisites, setup, and troubleshooting.
-->

# Deployment Guide

## Purpose
This guide explains how to deploy the SEIM system to production, including environment setup, deployment steps, and troubleshooting.

## Revision History
| Date       | Author              | Description                                 |
|------------|---------------------|---------------------------------------------|
| 2025-05-31 | Documentation Team  | Added template compliance, purpose, and revision history. |

## Table of Contents
- [Prerequisites](#prerequisites)
- [Production Environment Setup](#production-environment-setup)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment](#post-deployment)
- [Rollback](#rollback)
- [Troubleshooting](#troubleshooting)

## Prerequisites
- Docker and Docker Compose installed
- PostgreSQL 17 database
- Redis server for Celery
- Production environment variables set (see below)

## Production Environment Setup
- Set environment variables in `.env` or your deployment system:
  - `DJANGO_ENV=prod`
  - `DATABASE_URL=postgres://...`
  - `REDIS_URL=redis://...`
  - `SECRET_KEY=...`
  - `ALLOWED_HOSTS=your-domain.com`
  - `AWS_*` for S3 if using cloud storage

## Deployment Steps
1. Build and start containers:
   ```powershell
   docker-compose -f docker-compose.yml up -d --build
   ```
2. Run migrations:
   ```powershell
   docker-compose exec web python manage.py migrate
   ```
3. Collect static files:
   ```powershell
   docker-compose exec web python manage.py collectstatic --noinput
   ```
4. Create superuser (if needed):
   ```powershell
   docker-compose exec web python manage.py createsuperuser
   ```
5. Access the app at `http://your-domain.com`

## Post-Deployment
- Monitor logs: `docker-compose logs -f web`
- Check health endpoints: `/health/`
- Set up backups for database and media
- Configure SSL/TLS (via reverse proxy or cloud provider)

## Rollback
- To rollback, stop containers and restore from backup:
   ```powershell
   docker-compose down
   # Restore database and media files from backup
   docker-compose up -d
   ```

## Troubleshooting
- See [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common deployment issues.

---

_Last updated: 2025-05-31_
