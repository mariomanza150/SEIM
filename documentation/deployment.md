# SEIM Production Deployment Guide

This comprehensive guide covers deploying the SEIM (Student Exchange Information Manager) platform to a production environment using Docker, Gunicorn, Nginx, and secure secrets management.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Security](#security)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Backup & Recovery](#backup--recovery)

## Overview

The SEIM production deployment uses a containerized microservices architecture with the following components:

- **Django Web Application**: Served by Gunicorn WSGI server
- **PostgreSQL Database**: Primary data storage
- **Redis**: Caching and message broker
- **ClamAV**: Virus scanning service
- **Nginx**: Reverse proxy, static file serving, and SSL termination
- **Celery**: Background task processing
- **Fluentd**: Log aggregation (optional)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Internet    │    │      Nginx      │    │   Django/Gunicorn│
│                 │◄──►│  (Port 80/443)  │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Static Files  │    │   PostgreSQL    │
                       │   Media Files   │    │   (Port 5432)   │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                ┌───────────────────────┼───────────────────────┐
                                ▼                       ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │     ClamAV      │    │     Celery      │
                       │  (Port 6379)    │    │   (Port 3310)   │    │    Workers      │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores (4+ cores recommended)

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For code deployment
- **SSL Certificate**: For HTTPS (Let's Encrypt recommended)

### External Services

- **Domain Name**: Pointed to your server's IP address
- **Email Service**: SMTP server or AWS SES
- **File Storage**: AWS S3 or compatible storage (optional)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd seim

# Setup production environment
make prod-setup

# Generate secrets
make prod-secrets
```

### 2. Configure Environment

```bash
# Edit production configuration
nano .env.prod

# Configure your domain, email settings, and other variables
```

### 3. Deploy

```bash
# Build and deploy
make deploy-prod

# Check status
make prod-status

# View logs
make prod-logs
```

### 4. Verify Deployment

```bash
# Check health
make prod-health

# Visit your application
curl http://your-domain.com/health/
```

## Detailed Setup

### Step 1: Server Preparation

#### Install Docker and Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply group changes
```

#### Configure Firewall

```bash
# Ubuntu/Debian with UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL with firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Step 2: Application Setup

#### Clone Repository

```bash
git clone <repository-url>
cd seim
```

#### Initialize Production Environment

```bash
# Create production environment file
cp env.prod.example .env.prod

# Setup directories and generate secrets
make prod-setup
make prod-secrets
```

### Step 3: Configuration

#### Environment Variables (.env.prod)

Edit `.env.prod` with your production values:

```bash
# Domain configuration
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (passwords will be read from secrets)
POSTGRES_DB=seim
POSTGRES_USER=seimuser

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# AWS S3 (if using)
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name

# Scaling configuration
WEB_REPLICAS=2
CELERY_REPLICAS=2
```

#### Secrets Configuration

Create the following secret files in the `secrets/` directory:

```bash
# Django secret key (auto-generated)
secrets/django_secret_key.txt

# Database password (auto-generated)
secrets/db_password.txt

# Redis password (auto-generated)
secrets/redis_password.txt

# AWS credentials (manual)
echo "your-aws-access-key" > secrets/aws_access_key_id.txt
echo "your-aws-secret-key" > secrets/aws_secret_access_key.txt

# Email credentials (manual)
echo "your-email@domain.com" > secrets/email_host_user.txt
echo "your-email-password" > secrets/email_host_password.txt
```

#### SSL Configuration (Optional)

For HTTPS deployment:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Update nginx.conf to enable HTTPS
```

### Step 4: Deployment

#### Build and Deploy

```bash
# Build production images
make build-prod

# Deploy services
make deploy-prod
```

#### Initial Setup

```bash
# Create superuser
make prod-shell
python manage.py createsuperuser

# Create initial data
python manage.py create_initial_data

# Exit shell
exit
```

### Step 5: Verification

#### Health Checks

```bash
# Check all services
make prod-health

# Check specific endpoints
curl http://your-domain.com/health/
curl http://your-domain.com/api/
```

#### Service Status

```bash
# View running services
make prod-status

# View logs
make prod-logs
```

## Configuration

### Gunicorn Configuration

Gunicorn is configured with the following production-optimized settings:

```bash
# Workers
GUNICORN_WORKERS=3                    # 2 * CPU cores + 1
GUNICORN_WORKER_CLASS=sync            # sync for CPU-bound, gevent for I/O-bound
GUNICORN_WORKER_CONNECTIONS=1000      # Max connections per worker
GUNICORN_MAX_REQUESTS=1000            # Restart workers after N requests
GUNICORN_MAX_REQUESTS_JITTER=100      # Random jitter for restarts
GUNICORN_TIMEOUT=30                   # Request timeout
GUNICORN_KEEP_ALIVE=2                 # Keep-alive timeout
GUNICORN_LOG_LEVEL=info               # Log level
```

### Nginx Configuration

Nginx is configured with:

- **Rate Limiting**: API endpoints limited to 60 req/min, login to 10 req/min
- **Static File Serving**: Optimized caching for static assets
- **Security Headers**: XSS protection, content type sniffing prevention
- **Gzip Compression**: Enabled for text-based content
- **SSL Termination**: Ready for HTTPS configuration

### Database Configuration

PostgreSQL is configured with:

- **Health Checks**: Automatic restart on failure
- **Resource Limits**: 1GB memory limit, 512MB reservation
- **Backup Volume**: Persistent storage for database data
- **Connection Pooling**: Optimized for production load

### Redis Configuration

Redis is configured with:

- **Persistence**: AOF (Append Only File) enabled
- **Authentication**: Password-protected access
- **Resource Limits**: 512MB memory limit, 256MB reservation
- **Health Checks**: Ping-based health monitoring

## Security

### Secrets Management

All sensitive data is managed through Docker secrets:

```bash
# Secrets are stored as files in the secrets/ directory
secrets/
├── django_secret_key.txt
├── db_password.txt
├── redis_password.txt
├── aws_access_key_id.txt
├── aws_secret_access_key.txt
├── email_host_user.txt
└── email_host_password.txt
```

### Network Security

- **Internal Network**: All services communicate over a private Docker network
- **Port Exposure**: Only Nginx ports (80/443) are exposed to the internet
- **Firewall**: Configured to allow only necessary ports

### Application Security

- **HTTPS**: SSL/TLS termination at Nginx level
- **Security Headers**: Comprehensive security headers in Nginx
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Django's built-in security features
- **File Security**: ClamAV virus scanning for uploads

### Access Control

```bash
# File permissions
chmod 600 secrets/*.txt
chmod 644 .env.prod

# Directory permissions
chmod 755 secrets/
chmod 755 nginx/
```

## Monitoring & Maintenance

### Health Monitoring

```bash
# Check service health
make prod-health

# View service status
make prod-status

# Monitor logs
make prod-logs
```

### Log Management

Logs are available in the following locations:

```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs celery

# Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Database logs
docker-compose -f docker-compose.prod.yml logs db
```

### Performance Monitoring

Key metrics to monitor:

- **Response Time**: API endpoint response times
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Database Connections**: Active database connections
- **Cache Hit Rate**: Redis cache performance
- **Disk Usage**: Volume storage usage

### Updates and Maintenance

#### Application Updates

```bash
# Pull latest changes
git pull origin main

# Update production deployment
make deploy-prod-update

# Verify deployment
make prod-health
```

#### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart Docker services
sudo systemctl restart docker
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
make prod-logs

# Check service status
make prod-status

# Restart services
make prod-stop
make deploy-prod
```

#### Database Connection Issues

```bash
# Check database health
make prod-health

# Connect to database
make prod-shell
python manage.py dbshell
```

#### Static Files Not Loading

```bash
# Collect static files
make prod-shell
python manage.py collectstatic --noinput
exit

# Restart web service
docker-compose -f docker-compose.prod.yml restart web
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Adjust worker count in .env.prod
GUNICORN_WORKERS=2
WEB_REPLICAS=1
```

### Debug Mode

For debugging, temporarily enable debug mode:

```bash
# Edit .env.prod
DEBUG=true

# Restart services
make deploy-prod-update
```

### Log Analysis

```bash
# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx

# Filter logs by level
docker-compose -f docker-compose.prod.yml logs web | grep ERROR
```

## Backup & Recovery

### Automated Backups

#### Database Backup

```bash
# Create backup
make prod-backup

# Backups are stored in backups/YYYYMMDD_HHMMSS/
backups/
└── 20240101_120000/
    ├── database.sql
    └── media/
```

#### Manual Backup

```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U seimuser seim > backup.sql

# Media files backup
docker cp seim-web-prod:/app/media ./media-backup/
```

### Recovery

#### Database Recovery

```bash
# Restore from backup
make prod-restore

# Or manually
docker-compose -f docker-compose.prod.yml exec -T db psql -U seimuser -d seim < backup.sql
```

#### Full System Recovery

```bash
# Stop services
make prod-stop

# Restore data
make prod-restore

# Restart services
make deploy-prod
```

### Backup Automation

Create a cron job for automated backups:

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /path/to/seim && make prod-backup
```

## Production Checklist

### Pre-Deployment

- [ ] Server meets minimum requirements
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured
- [ ] Domain name configured
- [ ] SSL certificates obtained (if using HTTPS)
- [ ] Environment variables configured
- [ ] Secrets generated
- [ ] Email service configured
- [ ] File storage configured (if using S3)

### Deployment

- [ ] Repository cloned
- [ ] Production environment setup
- [ ] Secrets configured
- [ ] Services deployed
- [ ] Health checks passing
- [ ] SSL configured (if using HTTPS)
- [ ] Initial data created
- [ ] Superuser created

### Post-Deployment

- [ ] Application accessible via domain
- [ ] API endpoints responding
- [ ] Static files loading
- [ ] Email functionality working
- [ ] File uploads working
- [ ] Virus scanning functional
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Documentation updated

## Support

For deployment issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs: `make prod-logs`
3. Check service health: `make prod-health`
4. Consult the [developer guide](developer_guide.md)
5. Review [troubleshooting documentation](troubleshooting.md)

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

**Note**: This deployment guide assumes a basic understanding of Docker, Django, and system administration. For complex enterprise deployments, consider consulting with DevOps specialists or the development team.