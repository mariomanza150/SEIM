# SEIM Troubleshooting Guide

## Overview
This guide provides solutions to common issues encountered when setting up, running, and maintaining SEIM (Student Exchange Information Manager).

---

## 🔧 **Common Issues**

### **Dynforms Form Builder Issues**

#### **Issue**: Form Builder page loads but shows blank/empty UI
**Symptoms**: `/dynforms/` page loads but no form builder components are visible.

**Root Cause**: Usually caused by:
- Custom template overrides conflicting with official dynforms templates
- Missing template blocks (`pre_js` vs `extra_js`)
- Duplicate static files causing conflicts

**Solutions**:
1. **Use Official Templates Only**:
   ```bash
   # Remove any custom dynforms templates
   rm -f templates/dynforms/base.html
   
   # Remove local static files (use official package files)
   rm -rf static/dynforms/
   
   # Recollect static files
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. **Check Template Blocks**:
   - Ensure `templates/base.html` has `{% block pre_js %}{% endblock %}`
   - Official dynforms templates use `pre_js` block for JavaScript injection

3. **Verify Admin Access**:
   ```bash
   # Ensure admin user has admin role
   docker-compose exec web python manage.py shell -c "
   from accounts.models import User, Role
   admin_user = User.objects.get(username='admin')
   admin_role = Role.objects.get(name='admin')
   admin_user.roles.add(admin_role)
   print('Admin role assigned')
   "
   ```

4. **Test the Fix**:
   ```bash
   # Run the Selenium test
   docker-compose exec web pytest tests/selenium/test_dynforms_builder.py -v
   ```

**Prevention**: Always use official django-dynforms templates, JS, and CSS. Only override with CSS for styling (e.g., dark mode).

---

## 🐍 **Virtual Environment Issues**

### **Virtual Environment Setup Problems**

#### **Issue**: "No module named 'celery'" or similar import errors
**Symptoms**: Selenium E2E tests or local development tools fail with import errors.

**Root Cause**: Virtual environment not activated or dependencies not installed.

**Solutions**:
1. **Activate Virtual Environment**:
   ```bash
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   
   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   
   # Install all development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Verify Installation**:
   ```bash
   # Check if key packages are available
   python -c "import django; print(f'Django {django.get_version()}')"
   python -c "import selenium; print(f'Selenium {selenium.__version__}')"
   ```

#### **Issue**: Permission errors on Windows PowerShell
**Symptoms**: "Execution policy" errors when trying to activate virtual environment.

**Solutions**:
```bash
# Option 1: Run PowerShell as Administrator and set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Option 2: Use Command Prompt instead
.venv\Scripts\activate.bat

# Option 3: Use Git Bash (if available)
source .venv/Scripts/activate
```

#### **Issue**: Virtual environment not found
**Symptoms**: "The system cannot find the path specified" when trying to activate.

**Solutions**:
```bash
# 1. Check if virtual environment exists
ls .venv  # Linux/macOS
dir .venv  # Windows

# 2. If not found, recreate the virtual environment
rm -rf .venv  # Linux/macOS
rmdir /s .venv  # Windows

# 3. Create new virtual environment
python -m venv .venv

# 4. Activate and install dependencies
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements-dev.txt
```

#### **Issue**: Selenium tests fail with "Chrome not found"
**Symptoms**: Selenium tests fail with Chrome driver errors.

**Solutions**:
1. **Install Chrome Browser**:
   - Download and install Google Chrome from https://www.google.com/chrome/
   - Ensure Chrome is in your system PATH

2. **Use webdriver-manager** (automatic driver management):
   ```bash
   # Install webdriver-manager
   pip install webdriver-manager
   
   # Update your test code to use webdriver-manager
   from selenium import webdriver
   from webdriver_manager.chrome import ChromeDriverManager
   from selenium.webdriver.chrome.service import Service
   
   service = Service(ChromeDriverManager().install())
   driver = webdriver.Chrome(service=service)
   ```

3. **Manual ChromeDriver Setup**:
   ```bash
   # Download ChromeDriver manually
   # Visit: https://chromedriver.chromium.org/
   # Download version matching your Chrome browser
   # Add to PATH or place in project directory
   ```

#### **Issue**: Django server not accessible from Selenium tests
**Symptoms**: Selenium tests fail with connection refused errors.

**Solutions**:
```bash
# 1. Ensure Django server is running in Docker
docker-compose up -d

# 2. Check if server is accessible
curl http://localhost:8000/

# 3. Check Docker logs for errors
docker-compose logs web

# 4. Verify admin user exists
docker-compose exec web python manage.py shell -c "
from accounts.models import User
print('Admin user exists:', User.objects.filter(username='admin').exists())
"
```

### **Virtual Environment Best Practices**

#### **Workflow Checklist**:
```bash
# Before running E2E tests or local dev tools:
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 2. Verify Django server is running
docker-compose ps

# 3. Run your tests/tools
make test-selenium
# or
npx jest --config=jest.config.js

# 4. Deactivate when done
deactivate
```

#### **Common Commands**:
```bash
# Check virtual environment status
echo $VIRTUAL_ENV  # Should show path to .venv

# List installed packages
pip list

# Update dependencies
pip install -r requirements-dev.txt --upgrade

# Clean virtual environment
pip uninstall -y -r requirements-dev.txt
pip install -r requirements-dev.txt
```

---

## 🚨 **Emergency Procedures**

### **System Down - Quick Recovery**
```bash
# 1. Check if containers are running
docker-compose ps

# 2. Restart all services
docker-compose down
docker-compose up -d

# 3. Check logs for errors
docker-compose logs -f web
```

### **Database Issues - Emergency Recovery**
```bash
# 1. Check database connection
docker-compose exec db pg_isready -U postgres

# 2. Restart database only
docker-compose restart db

# 3. Check database logs
docker-compose logs db
```

---

## 🐳 **Docker Issues**

### **Container Won't Start**

#### **Issue**: Container fails to start
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs web
docker-compose logs db
docker-compose logs redis
```

#### **Solutions**:
1. **Port Conflicts**:
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :5432
   
   # Stop conflicting services
   sudo systemctl stop postgresql
   sudo systemctl stop redis
   ```

2. **Insufficient Resources**:
   ```bash
   # Check Docker resources
   docker system df
   
   # Clean up unused resources
   docker system prune -a
   ```

3. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod +x scripts/*.sh
   ```

### **Container Health Checks**

#### **Check All Services**:
```bash
# Check web service
docker-compose exec web python manage.py check

# Check database
docker-compose exec db pg_isready -U postgres

# Check Redis
docker-compose exec redis redis-cli ping
```

#### **Service-Specific Issues**:

**Web Service**:
```bash
# Check Django settings
docker-compose exec web python manage.py check --deploy

# Check for missing migrations
docker-compose exec web python manage.py showmigrations

# Check static files
docker-compose exec web python manage.py collectstatic --dry-run
```

**Database Service**:
```bash
# Check database size
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('seim_db'));"

# Check active connections
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Check database locks
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

**Redis Service**:
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Check Redis keys
docker-compose exec redis redis-cli keys "*"

# Clear Redis cache if needed
docker-compose exec redis redis-cli flushall
```

---

## 🗄️ **Database Issues**

### **Connection Errors**

#### **Issue**: "Connection refused" or "Connection timeout"
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
docker-compose exec web python manage.py dbshell
```

#### **Solutions**:
1. **Database not started**:
   ```bash
   docker-compose up -d db
   ```

2. **Wrong credentials**:
   ```bash
   # Check environment variables
   docker-compose exec web env | grep DATABASE
   
   # Verify .env file
   cat .env | grep DATABASE
   ```

3. **Database corrupted**:
   ```bash
   # Backup current data
   docker-compose exec db pg_dump -U postgres seim_db > backup.sql
   
   # Recreate database
   docker-compose exec db dropdb -U postgres seim_db
   docker-compose exec db createdb -U postgres seim_db
   
   # Restore from backup
   docker-compose exec db psql -U postgres seim_db < backup.sql
   ```

### **Migration Issues**

#### **Issue**: "No migrations to apply" or "Migration conflicts"
```bash
# Check migration status
docker-compose exec web python manage.py showmigrations

# Check for unapplied migrations
docker-compose exec web python manage.py migrate --plan
```

#### **Solutions**:
1. **Reset migrations** (⚠️ **DESTRUCTIVE**):
   ```bash
   # Only use in development!
   docker-compose exec web python manage.py migrate --fake-initial
   ```

2. **Fix migration conflicts**:
   ```bash
   # Mark migrations as applied
   docker-compose exec web python manage.py migrate --fake
   
   # Or reset to specific migration
   docker-compose exec web python manage.py migrate exchange 0001 --fake
   ```

3. **Create new migration**:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

### **Performance Issues**

#### **Slow Queries**:
```bash
# Enable query logging
docker-compose exec db psql -U postgres -c "ALTER SYSTEM SET log_statement = 'all';"
docker-compose exec db psql -U postgres -c "SELECT pg_reload_conf();"

# Check slow queries
docker-compose exec db psql -U postgres -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

#### **Database Size**:
```bash
# Check table sizes
docker-compose exec db psql -U postgres -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 📧 **Email Issues**

### **Email Not Sending**

#### **Issue**: Emails not being sent or received
```bash
# Check email configuration
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_HOST:', getattr(settings, 'EMAIL_HOST', 'Not set'))
print('EMAIL_PORT:', getattr(settings, 'EMAIL_PORT', 'Not set'))
"
```

#### **Solutions**:

1. **SMTP Configuration**:
   ```bash
   # Test SMTP connection
   docker-compose exec web python manage.py shell -c "
   from django.core.mail import send_mail
   try:
       send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
       print('Email sent successfully')
   except Exception as e:
       print('Email error:', e)
   "
   ```

2. **Gmail App Password**:
   - Enable 2-factor authentication
   - Generate app-specific password
   - Use app password in EMAIL_HOST_PASSWORD

3. **AWS SES Configuration**:
   ```bash
   # Install AWS SES
   docker-compose exec web pip install django-ses
   
   # Update settings
   EMAIL_BACKEND = 'django_ses.SESBackend'
   AWS_SES_REGION_NAME = 'us-east-1'
   AWS_SES_ACCESS_KEY_ID = 'your-access-key'
   AWS_SES_SECRET_ACCESS_KEY = 'your-secret-key'
   ```

### **Email Queue Issues**

#### **Issue**: Emails stuck in queue
```bash
# Check Celery worker status
docker-compose exec web celery -A seim inspect active

# Check queue status
docker-compose exec web celery -A seim inspect stats

# Clear email queue
docker-compose exec web celery -A seim purge
```

---

## 🔐 **Authentication Issues**

### **Login Problems**

#### **Issue**: Users can't log in
```bash
# Check user account status
docker-compose exec web python manage.py shell -c "
from accounts.models import User
users = User.objects.all()
for user in users:
    print(f'{user.username}: active={user.is_active}, verified={user.is_email_verified}')
"
```

#### **Solutions**:
1. **Account locked**:
   ```bash
   # Unlock account
   docker-compose exec web python manage.py shell -c "
   from accounts.models import User
   user = User.objects.get(username='username')
   user.failed_login_attempts = 0
   user.locked_until = None
   user.save()
   print('Account unlocked')
   "
   ```

2. **Email not verified**:
   ```bash
   # Verify email manually
   docker-compose exec web python manage.py shell -c "
   from accounts.models import User
   user = User.objects.get(username='username')
   user.is_email_verified = True
   user.save()
   print('Email verified')
   "
   ```

3. **Password reset**:
   ```bash
   # Reset password
   docker-compose exec web python manage.py shell -c "
   from accounts.models import User
   user = User.objects.get(username='username')
   user.set_password('newpassword123')
   user.save()
   print('Password reset')
   "
   ```

### **JWT Token Issues**

#### **Issue**: API authentication failing
```bash
# Check JWT settings
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('JWT_ACCESS_TOKEN_LIFETIME:', getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 'Not set'))
print('JWT_REFRESH_TOKEN_LIFETIME:', getattr(settings, 'JWT_REFRESH_TOKEN_LIFETIME', 'Not set'))
"
```

#### **Solutions**:
1. **Token expired**:
   - Use refresh token to get new access token
   - Increase token lifetime in settings

2. **Invalid token**:
   - Clear browser storage
   - Log out and log back in

---

## 📁 **File Upload Issues**

### **Document Upload Problems**

#### **Issue**: Files not uploading or processing
```bash
# Check file permissions
ls -la media/
ls -la staticfiles/

# Check disk space
df -h

# Check file size limits
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('FILE_UPLOAD_MAX_MEMORY_SIZE:', getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 'Not set'))
print('DATA_UPLOAD_MAX_MEMORY_SIZE:', getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 'Not set'))
"
```

#### **Solutions**:
1. **Permission issues**:
   ```bash
   # Fix permissions
   sudo chown -R www-data:www-data media/
   sudo chmod -R 755 media/
   ```

2. **Disk space**:
   ```bash
   # Clean up old files
   docker-compose exec web python manage.py shell -c "
   from documents.models import Document
   old_docs = Document.objects.filter(created_at__lt='2024-01-01')
   print(f'Old documents: {old_docs.count()}')
   # old_docs.delete()  # Uncomment to delete
   "
   ```

3. **File size limits**:
   ```python
   # settings/base.py
   FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
   ```

### **Static Files Issues**

#### **Issue**: CSS/JS files not loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check static files
ls -la staticfiles/

# Check web server configuration
docker-compose exec web python manage.py shell -c "
from django.conf import settings
print('STATIC_URL:', settings.STATIC_URL)
print('STATIC_ROOT:', settings.STATIC_ROOT)
print('STATICFILES_DIRS:', settings.STATICFILES_DIRS)
"
```

---

## 🎨 **Frontend Issues**

### **JavaScript Errors**

#### **Issue**: Console errors or broken functionality
```bash
# Check JavaScript files
ls -la static/js/

# Check for syntax errors
npx eslint static/js/

# Run frontend tests
npx jest --config=jest.config.js
```

#### **Solutions**:
1. **Browser cache**:
   - Clear browser cache
   - Hard refresh (Ctrl+F5)

2. **JavaScript errors**:
   ```bash
   # Check for syntax errors
   node -c static/js/main.js
   
   # Run linter
   npx eslint static/js/ --fix
   ```

3. **API errors**:
   - Check browser network tab
   - Verify API endpoints are working
   - Check authentication tokens

### **CSS Issues**

#### **Issue**: Styling problems or broken layout
```bash
# Check CSS files
ls -la static/css/

# Compile CSS if using preprocessors
npm run build-css

# Check for CSS errors
npx stylelint static/css/
```

#### **Solutions**:
1. **Bootstrap issues**:
   - Verify Bootstrap is loaded
   - Check for CSS conflicts

2. **Responsive issues**:
   - Test on different screen sizes
   - Check viewport meta tag

---

## 🔧 **Performance Issues**

### **Slow Page Loads**

#### **Issue**: Pages taking too long to load
```bash
# Check database queries
docker-compose exec web python manage.py shell -c "
from django.db import connection
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    # Your code here
    pass

for query in connection.queries:
    print(f'{query[\"time\"]}s: {query[\"sql\"]}')
"
```

#### **Solutions**:
1. **Database optimization**:
   ```bash
   # Add database indexes
   docker-compose exec web python manage.py shell -c "
   from django.db import connection
   cursor = connection.cursor()
   cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_user(email);')
   cursor.execute('CREATE INDEX IF NOT EXISTS idx_application_status ON exchange_application(status);')
   "
   ```

2. **Caching**:
   ```bash
   # Check cache status
   docker-compose exec web python manage.py shell -c "
   from django.core.cache import cache
   cache.set('test', 'value', 60)
   print('Cache test:', cache.get('test'))
   "
   ```

3. **Static file optimization**:
   ```bash
   # Compress static files
   docker-compose exec web python manage.py compress
   ```

### **Memory Issues**

#### **Issue**: High memory usage
```bash
# Check container memory usage
docker stats

# Check Python memory usage
docker-compose exec web python manage.py shell -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

#### **Solutions**:
1. **Restart services**:
   ```bash
   docker-compose restart web
   docker-compose restart celery
   ```

2. **Optimize queries**:
   ```python
   # Use select_related and prefetch_related
   applications = Application.objects.select_related('student', 'program').all()
   ```

---

## 📊 **Monitoring and Logs**

### **Log Analysis**

#### **View Logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f celery

# Recent logs
docker-compose logs --tail=100 web
```

#### **Error Patterns**:
```bash
# Find errors in logs
docker-compose logs web | grep -i error

# Find warnings
docker-compose logs web | grep -i warning

# Find specific errors
docker-compose logs web | grep -i "database connection"
```

### **Health Checks**

#### **System Health**:
```bash
# Check all services
make health-check

# Check specific components
docker-compose exec web python manage.py check --deploy
docker-compose exec db pg_isready -U postgres
docker-compose exec redis redis-cli ping
```

#### **Performance Monitoring**:
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/"

# Monitor database performance
docker-compose exec db psql -U postgres -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"
```

---

## 🔄 **Backup and Recovery**

### **Database Backup**

#### **Create Backup**:
```bash
# Full database backup
docker-compose exec db pg_dump -U postgres seim_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific tables
docker-compose exec db pg_dump -U postgres -t accounts_user -t exchange_program seim_db > users_programs_backup.sql
```

#### **Restore Backup**:
```bash
# Restore full backup
docker-compose exec db psql -U postgres seim_db < backup_20241201_120000.sql

# Restore specific tables
docker-compose exec db psql -U postgres seim_db < users_programs_backup.sql
```

### **File Backup**

#### **Backup Media Files**:
```bash
# Create archive
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Backup to remote location
rsync -avz media/ backup-server:/backups/seim/media/
```

#### **Restore Files**:
```bash
# Extract archive
tar -xzf media_backup_20241201_120000.tar.gz

# Restore from remote
rsync -avz backup-server:/backups/seim/media/ media/
```

---

## 🆘 **Getting Help**

### **Self-Service Resources**
- [Installation Guide](installation.md)
- [Admin Guide](admin_guide.md)
- [Developer Guide](developer_guide.md)
- [API Documentation](api_documentation.md)

### **Log Collection**
```bash
# Collect diagnostic information
docker-compose exec web python manage.py shell -c "
import sys
import django
print('Python version:', sys.version)
print('Django version:', django.get_version())
print('Database:', django.conf.settings.DATABASES['default']['ENGINE'])
"

# Collect logs
docker-compose logs > seim_logs_$(date +%Y%m%d_%H%M%S).txt

# Collect system info
docker system info > docker_info_$(date +%Y%m%d_%H%M%S).txt
```

### **Contact Information**
- **Documentation**: Check this guide first
- **GitHub Issues**: Report bugs and feature requests
- **Email Support**: admin@seim.local (for critical issues)

---

## 📋 **Quick Reference**

### **Common Commands**
```bash
# Restart everything
docker-compose down && docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Run tests
make test

# Backup database
docker-compose exec db pg_dump -U postgres seim_db > backup.sql
```

### **Emergency Contacts**
- **System Admin**: admin@seim.local
- **Database Admin**: db-admin@seim.local
- **Emergency Hotline**: +1-555-EMERGENCY

---

**Last Updated**: December 2024  
**Version**: 1.0 