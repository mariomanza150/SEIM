<!--
File: docs/TROUBLESHOOTING.md
Title: Troubleshooting Guide
Purpose: Provide solutions and diagnostic steps for common issues encountered in the SEIM system.
-->

# Troubleshooting Guide

## Purpose
This guide helps resolve common issues with the SEIM system, including environment, deployment, and runtime errors.

## Revision History
| Date       | Author              | Description                                 |
|------------|---------------------|---------------------------------------------|
| 2025-05-31 | Documentation Team  | Added template compliance, title, purpose, and revision history. |

## Common Issues

### 1. Docker Container Issues

#### Problem: Containers won't start
```bash
docker-compose up
# Error: Cannot start service web: driver failed programming external connectivity
```

**Solution:**
```bash
# Stop all containers
docker-compose down

# Remove all containers
docker rm -f $(docker ps -aq)

# Restart Docker service
# On Windows:
Restart-Service docker
# On Linux:
sudo systemctl restart docker

# Try again
docker-compose up --build
```

#### Problem: Database connection errors
```
django.db.utils.OperationalError: could not connect to server: Connection refused
```

**Solution:**
```bash
# Check if database container is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database container
docker-compose restart db

# Check environment variables
cat .env | grep POSTGRES
```

### 2. Migration Issues

#### Problem: Migration conflicts
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
```bash
# Reset migrations (DEVELOPMENT ONLY)
docker-compose exec web python manage.py migrate exchange zero
docker-compose exec web python manage.py migrate

# For production, create a data migration
docker-compose exec web python manage.py makemigrations --merge
```

#### Problem: Column already exists
```
django.db.utils.ProgrammingError: column "field_name" already exists
```

**Solution:**
```bash
# Check migration status
docker-compose exec web python manage.py showmigrations

# Fake the problematic migration
docker-compose exec web python manage.py migrate exchange 0001 --fake

# Apply remaining migrations
docker-compose exec web python manage.py migrate
```

### 3. Authentication Issues

#### Problem: JWT token not working
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution:**
1. Check token format:
```bash
# Correct format
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Common mistakes
Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...  # Missing "Bearer"
Authorization: bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...  # Lowercase "bearer"
```

2. Verify token expiration:
```python
# In Django shell
import jwt
from django.conf import settings

token = "your-token-here"
try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    print(f"Token expires at: {payload['exp']}")
except jwt.ExpiredSignatureError:
    print("Token has expired")
```

#### Problem: Permission denied errors
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Solution:**
```python
# Check user permissions in Django shell
docker-compose exec web python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(email='user@example.com')
print(user.groups.all())
print(user.user_permissions.all())
print(user.is_manager)
```

### 4. File Upload Issues

#### Problem: File too large
```
413 Request Entity Too Large
```

**Solution:**
1. Check Django settings:
```python
# settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
```

2. Check nginx configuration (if using):
```nginx
# nginx.conf
client_max_body_size 10M;
```

#### Problem: File integrity check fails
```json
{
  "error": "File integrity check failed"
}
```

**Solution:**
```python
# Check file hash manually
import hashlib

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# In Django shell
from exchange.models import Document
doc = Document.objects.get(id=1)
print(f"Stored hash: {doc.file_hash}")
print(f"Actual hash: {calculate_file_hash(doc.file.path)}")
```

### 5. Form Submission Issues

#### Problem: Form data not saving
```json
{
  "error": "Invalid form data"
}
```

**Solution:**
1. Check form field configuration:
```python
# Django shell
from exchange.models import FormStep
step = FormStep.objects.get(step_number=1)
print(step.fields)
```

2. Validate data format:
```python
import json
from exchange.services.form_handler import FormHandler

# Check if JSON is valid
data = '{"field": "value"}'
try:
    json.loads(data)
    print("Valid JSON")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

### 6. Email Issues

#### Problem: Emails not sending
```
SMTPAuthenticationError: (535, b'Authentication failed')
```

**Solution:**
1. Check email settings:
```python
# .env file
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Not your regular password!
```

2. Test email configuration:
```python
# Django shell
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Subject',
    'Test message',
    settings.EMAIL_HOST_USER,
    ['recipient@example.com'],
    fail_silently=False,
)
```

### 7. Performance Issues

#### Problem: Slow API responses
**Solution:**
1. Check database queries:
```python
# settings.py (temporarily)
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

2. Use select_related and prefetch_related:
```python
# views.py
queryset = Exchange.objects.select_related('student').prefetch_related('documents')
```

3. Add database indexes:
```python
# models.py
class Exchange(models.Model):
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['student', 'status']),
        ]
```

### 8. Development Environment Issues

#### Problem: Hot reloading not working
**Solution:**
```yaml
# docker-compose.yml
services:
  web:
    volumes:
      - .:/app  # Ensure this is present
    environment:
      - PYTHONUNBUFFERED=1
```

#### Problem: Can't connect to localhost:8000
**Solution:**
1. Check if container is running:
```bash
docker-compose ps
```

2. Check port mapping:
```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "8000:8000"
```

3. Check Windows firewall (if applicable)

### 9. Testing Issues

#### Problem: Tests failing locally but passing in CI
**Solution:**
1. Ensure same database state:
```bash
# Reset test database
docker-compose exec web python manage.py flush --no-input
```

2. Check for timezone issues:
```python
# settings.py
USE_TZ = True
TIME_ZONE = 'UTC'
```

3. Clear cache:
```python
from django.core.cache import cache
cache.clear()
```

### 10. Production Issues

#### Problem: Static files not serving
**Solution:**
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check nginx config
location /static/ {
    alias /app/static/;
}
```

#### Problem: SSL certificate errors
**Solution:**
1. Check certificate expiration:
```bash
openssl x509 -enddate -noout -in /path/to/cert.pem
```

2. Verify certificate chain:
```bash
openssl verify -CAfile /path/to/ca.pem /path/to/cert.pem
```

## Debug Mode

### Enable Debug Mode (Development Only)
```python
# .env
DEBUG=True
DJANGO_DEBUG_TOOLBAR=True

# settings.py
if DEBUG and env.bool('DJANGO_DEBUG_TOOLBAR', False):
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Using Django Shell
```bash
# Access Django shell
docker-compose exec web python manage.py shell_plus

# Import all models automatically
from exchange.models import *
from django.contrib.auth import get_user_model
User = get_user_model()

# Quick debugging
exchange = Exchange.objects.first()
print(exchange.__dict__)
```

### Logging

#### Enable detailed logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'exchange': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

#### View logs
```bash
# View application logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100 web
```

## Emergency Procedures

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U seim_user seim > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U seim_user seim < backup.sql
```

### Reset Everything (Development Only)
```bash
# Stop all containers
docker-compose down -v

# Remove all images
docker rmi $(docker images -q)

# Clean build cache
docker builder prune -a

# Start fresh
docker-compose up --build
```

### Roll Back Migration
```bash
# Check current migration
docker-compose exec web python manage.py showmigrations exchange

# Roll back to specific migration
docker-compose exec web python manage.py migrate exchange 0003

# Roll back all migrations for an app
docker-compose exec web python manage.py migrate exchange zero
```

## Getting Help

### 1. Check Logs
Always check logs first:
- Application logs: `docker-compose logs web`
- Database logs: `docker-compose logs db`
- Nginx logs: `docker-compose logs nginx`

### 2. Enable Debug Mode
For development environments, enable debug mode to see detailed error messages.

### 3. Search Error Messages
Copy the exact error message and search:
- Project documentation
- Django documentation
- Stack Overflow
- GitHub issues

### 4. Create Minimal Reproduction
When reporting issues:
1. Create minimal code that reproduces the issue
2. Include error messages and logs
3. Specify environment details
4. List steps to reproduce

### 5. Contact Support
- GitHub Issues: For bugs and feature requests
- Discussions: For questions and help
- Email: support@seim-project.org

## Useful Commands

### Docker Commands
```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs <container_id>

# Execute command in container
docker exec -it <container_id> /bin/bash

# Copy files from container
docker cp <container_id>:/path/to/file ./local/path
```

### Django Commands
```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Database shell
docker-compose exec web python manage.py dbshell

# Check deployment
docker-compose exec web python manage.py check --deploy

# Clear cache
docker-compose exec web python manage.py clear_cache
```

## Prevention Tips

1. **Always use version control**
2. **Test changes locally first**
3. **Keep backups before major changes**
4. **Document unusual configurations**
5. **Monitor logs regularly**
6. **Update dependencies carefully**
7. **Use staging environment**
8. **Implement monitoring and alerts**

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Documentation](https://docs.python.org/)

## Common Error Reference

### HTTP Status Codes
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server-side error

### Django Errors
- `DoesNotExist`: Object not found in database
- `MultipleObjectsReturned`: Query returned multiple objects
- `ValidationError`: Data validation failed
- `PermissionDenied`: User lacks required permission
- `ImproperlyConfigured`: Settings misconfiguration

### Database Errors
- `OperationalError`: Database connection issues
- `IntegrityError`: Constraint violation
- `DataError`: Invalid data type
- `ProgrammingError`: SQL syntax error

## Performance Optimization

### Database Optimization
```python
# Use only() for specific fields
exchanges = Exchange.objects.only('id', 'status', 'created_at')

# Use defer() to exclude fields
exchanges = Exchange.objects.defer('large_text_field')

# Bulk operations
Exchange.objects.bulk_create([
    Exchange(student=user1, status='draft'),
    Exchange(student=user2, status='draft'),
])

# Raw SQL for complex queries
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM exchange_exchange WHERE status = %s", ['approved'])
    results = cursor.fetchall()
```

### Caching
```python
# Redis caching
from django.core.cache import cache

def get_exchange_count(status):
    cache_key = f'exchange_count_{status}'
    count = cache.get(cache_key)
    
    if count is None:
        count = Exchange.objects.filter(status=status).count()
        cache.set(cache_key, count, 300)  # Cache for 5 minutes
    
    return count

# View-level caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def exchange_list(request):
    # View implementation
```

### Query Optimization
```python
# Avoid N+1 queries
# Bad:
for exchange in Exchange.objects.all():
    print(exchange.student.email)  # Queries database each time

# Good:
for exchange in Exchange.objects.select_related('student'):
    print(exchange.student.email)  # Single query

# Use exists() instead of count() when checking existence
# Bad:
if Exchange.objects.filter(student=user).count() > 0:
    # Has exchanges

# Good:
if Exchange.objects.filter(student=user).exists():
    # Has exchanges
```

## Security Checklist

### Development
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in development
- [ ] Test with different user roles
- [ ] Validate all input data
- [ ] Check for SQL injection vulnerabilities

### Production
- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set secure headers
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities
- [ ] Implement rate limiting

## Monitoring Checklist

### Application Monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] API response times
- [ ] Database query performance
- [ ] Background job monitoring

### Infrastructure Monitoring
- [ ] Server resources (CPU, RAM, Disk)
- [ ] Database connections
- [ ] Cache hit rates
- [ ] Queue lengths
- [ ] SSL certificate expiration

### Business Metrics
- [ ] User registrations
- [ ] Application submissions
- [ ] Processing times
- [ ] Error rates
- [ ] User satisfaction

This troubleshooting guide should help resolve most common issues with the SEIM system. Always remember to check logs first, and don't hesitate to reach out for support when needed.
