# Phase 2 Features - Deployment Guide

## 🚀 **Quick Start Deployment**

This guide covers deploying the Phase 2 critical features to production.

---

## 📋 **Pre-Deployment Checklist**

- [ ] All dependencies installed (`requirements.txt` updated)
- [ ] Environment variables configured
- [ ] Database migrations created and applied
- [ ] Docker Compose updated for ASGI
- [ ] Celery Beat configured
- [ ] Nginx configured for WebSocket (production)
- [ ] Tests passing

---

## 🔧 **Step-by-Step Deployment**

### **Step 1: Install Dependencies**

```bash
# Inside Docker container
docker-compose exec web pip install -r requirements.txt

# Or rebuild container
docker-compose build web
```

**New dependencies:**
- channels==4.0.0
- channels-redis==4.1.0
- daphne==4.0.0

---

### **Step 2: Configure Environment Variables**

Add to your `.env` file:

```bash
# WebSocket Configuration
WEBSOCKET_ENABLED=True
WEBSOCKET_RECONNECT_INTERVAL=5000

# Feature Flags
FEATURE_WEBSOCKET_NOTIFICATIONS=True
FEATURE_ADVANCED_SEARCH=True
FEATURE_CALENDAR_VIEW=True
FEATURE_NOTIFICATION_CENTER=True
```

---

### **Step 3: Create and Apply Database Migrations**

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations exchange
docker-compose exec web python manage.py makemigrations notifications
docker-compose exec web python manage.py makemigrations accounts

# Review migrations
docker-compose exec web python manage.py showmigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Verify
docker-compose exec web python manage.py showmigrations
```

**Expected migrations:**
- `exchange` - Add SavedSearch model
- `notifications` - Add Reminder model, add category field to Notification
- `accounts` - Add high_contrast and reduce_motion to UserSettings

---

### **Step 4: Update Docker Compose for ASGI**

#### **Option A: Development (Django runserver - basic WebSocket support)**

```yaml
# docker-compose.yml (current - works for development)
web:
  command: bash -c "/app/scripts/wait-for-db.sh && python manage.py runserver 0.0.0.0:8000"
```

Django's runserver has basic ASGI support, so WebSockets will work for development.

#### **Option B: Production (Daphne - full ASGI server)**

```yaml
# docker-compose.yml or docker-compose.prod.yml
web:
  command: bash -c "/app/scripts/wait-for-db.sh && daphne -b 0.0.0.0 -p 8000 seim.asgi:application"
```

**Or create a separate production compose file:**

```bash
# Create docker-compose.override.yml for production
cat > docker-compose.override.yml << 'EOF'
services:
  web:
    command: daphne -b 0.0.0.0 -p 8000 seim.asgi:application
EOF
```

---

### **Step 5: Configure Celery Beat for Reminders**

#### **Update `seim/celery.py`:**

Add this to your Celery configuration:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Send deadline reminders every 15 minutes
    'send-deadline-reminders': {
        'task': 'notifications.tasks.send_deadline_reminders',
        'schedule': crontab(minute='*/15'),
        'options': {'expires': 600}
    },
}
```

#### **Ensure Celery Beat is running:**

Check your docker-compose.yml has:

```yaml
celery-beat:
  build: .
  command: celery -A core.celery beat --loglevel=info
  depends_on:
    - redis
    - db
  env_file:
    - .env
```

---

### **Step 6: Restart Services**

```bash
# Stop services
docker-compose down

# Rebuild if needed
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f web
docker-compose logs -f celery-beat
```

---

### **Step 7: Verify Deployment**

#### **A. Test WebSocket Connection:**
1. Open browser to `http://localhost:8000/`
2. Login as any user
3. Open browser console (F12)
4. Look for: `WebSocket: Connected successfully`

#### **B. Test Real-time Notifications:**
1. Trigger a notification (e.g., update application status)
2. Toast should appear in bottom-right
3. Bell icon badge should update
4. Check notification center offcanvas

#### **C. Test Advanced Search:**
1. Navigate to Programs or Applications page
2. Apply filters
3. Save search
4. Apply saved search from dropdown

#### **D. Test Calendar:**
1. Navigate to `/calendar/`
2. Verify events appear
3. Click on event to navigate
4. Try different views (Month/Week/Day/List)

#### **E. Test Preferences:**
1. Navigate to `/preferences/`
2. Change theme, font size
3. Enable high contrast or reduce motion
4. Verify changes apply immediately

---

## 🔒 **Production Configuration**

### **Nginx WebSocket Proxy**

Add to your `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Regular HTTP traffic
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket traffic
    location /ws/ {
        proxy_pass http://web:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;  # 24 hours
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }
    
    # Media files
    location /media/ {
        alias /app/media/;
    }
}
```

### **SSL/TLS (HTTPS):**

For secure WebSocket connections (wss://), add SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    # ... rest of configuration above
}
```

---

## 🧪 **Testing in Production**

### **Test WebSocket Connection:**

```javascript
// Open browser console on production site
const ws = new WebSocket('wss://your-domain.com/ws/notifications/?token=YOUR_JWT_TOKEN');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => console.error('Error:', e);
```

### **Test Reminders:**

```bash
# Manually trigger reminder task
docker-compose exec web python manage.py shell
>>> from notifications.tasks import send_deadline_reminders
>>> send_deadline_reminders()
```

---

## 🔍 **Troubleshooting**

### **WebSocket Connection Fails:**

**Issue:** "WebSocket connection to 'ws://localhost:8000/ws/notifications/' failed"

**Solutions:**
1. Verify ASGI application is running (not WSGI)
2. Check if channels and channels-redis are installed
3. Verify Redis is running: `docker-compose exec redis redis-cli ping`
4. Check channel layer config in settings
5. Look for errors in web service logs: `docker-compose logs web`

### **Notifications Not Real-time:**

**Issue:** Notifications only appear on page refresh

**Solutions:**
1. Check if WebSocket is connected (browser console)
2. Verify FEATURE_WEBSOCKET_NOTIFICATIONS=True
3. Check if NotificationService._broadcast_notification is being called
4. Check Redis channel layer is working

### **Reminders Not Sending:**

**Issue:** Deadline reminders are not sent automatically

**Solutions:**
1. Verify Celery Beat is running: `docker-compose ps celery-beat`
2. Check Celery Beat logs: `docker-compose logs celery-beat`
3. Verify beat schedule is configured
4. Check if reminders exist in database: `Reminder.objects.filter(sent=False, remind_at__lte=now())`

### **Calendar Events Not Loading:**

**Issue:** Calendar shows no events

**Solutions:**
1. Check API endpoint: `curl http://localhost:8000/api/calendar/events/`
2. Verify JWT token is valid
3. Check if programs exist in database
4. Look for JavaScript errors in browser console
5. Verify FullCalendar.js is loaded

### **Search Filters Not Working:**

**Issue:** Filters don't filter results

**Solutions:**
1. Verify FilterSets are registered in ViewSets
2. Check if django-filter is installed
3. Look for API errors in network tab
4. Verify filter parameters are being sent
5. Check ViewSet filterset_class is set

---

## 📊 **Performance Monitoring**

### **WebSocket Health:**

```bash
# Check active WebSocket connections
docker-compose exec redis redis-cli
> PUBSUB CHANNELS
> PUBSUB NUMSUB notifications_*
```

### **Monitor Celery Tasks:**

```bash
# View Celery Beat schedule
docker-compose exec celery-beat celery -A core.celery inspect scheduled

# View active tasks
docker-compose exec celery-worker celery -A core.celery inspect active
```

### **Check Notification Queue:**

```bash
# Count pending reminders
docker-compose exec web python manage.py shell
>>> from notifications.models import Reminder
>>> from django.utils import timezone
>>> Reminder.objects.filter(sent=False, remind_at__lte=timezone.now()).count()
```

---

## 🔐 **Security Considerations**

### **WebSocket Authentication:**
- ✅ JWT tokens validated on connection
- ✅ Session authentication supported
- ✅ Per-user channels (isolated)
- ✅ CORS and CSRF protection

### **API Security:**
- ✅ All endpoints require authentication
- ✅ User isolation (users only see their own data)
- ✅ Rate limiting enabled
- ✅ XSS protection in all outputs

### **Production Checklist:**
- [ ] Use WSS (secure WebSocket) with SSL/TLS
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Configure CSRF_TRUSTED_ORIGINS
- [ ] Use strong SECRET_KEY
- [ ] Enable security middleware
- [ ] Set up firewall rules

---

## 📈 **Scaling Considerations**

### **WebSocket Scaling:**

For multiple web servers, use Redis channel layer (already configured):

```python
# settings/base.py (already configured)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://redis:6379/2")],
        },
    },
}
```

### **Load Balancing:**

When using multiple web servers with Nginx:

```nginx
upstream web_backends {
    least_conn;  # Use least connection algorithm
    server web1:8000;
    server web2:8000;
    server web3:8000;
}

location / {
    proxy_pass http://web_backends;
}

# WebSocket needs to stick to same backend
location /ws/ {
    proxy_pass http://web_backends;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # Add sticky session if needed
}
```

---

## 🎯 **Success Metrics**

After deployment, monitor these metrics:

### **WebSocket Health:**
- Connection success rate > 99%
- Reconnection time < 5 seconds
- Active connections count
- Message delivery rate

### **Notification Performance:**
- Notification delivery time < 100ms
- Email sending success rate > 95%
- Reminder accuracy (sent within 1 minute of scheduled time)

### **Search Performance:**
- Search response time < 200ms
- Filter apply time < 100ms
- Full-text search accuracy

### **Calendar Performance:**
- Event load time < 500ms
- API response time < 200ms

### **Accessibility:**
- Lighthouse accessibility score > 95
- WCAG 2.1 AA compliance: 100%
- Keyboard navigation: All features accessible

---

## 📞 **Support**

### **Documentation:**
- Complete Implementation: `PHASE2_COMPLETE.md`
- Backend Details: `PHASE2_BACKEND_IMPLEMENTATION_SUMMARY.md`
- Progress Report: `PHASE2_IMPLEMENTATION_PROGRESS.md`

### **Code Documentation:**
- All modules have comprehensive docstrings
- Inline comments explain complex logic
- API endpoints documented in code

### **Logs:**
```bash
# View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f web
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

---

## ✅ **Post-Deployment Verification**

After deployment, verify each feature:

### **1. WebSocket Notifications:**
```bash
# Check browser console for connection message
# Expected: "WebSocket: Connected successfully"
```

### **2. Notification Center:**
- Click bell icon in navbar
- Verify offcanvas opens
- Create test notification
- Verify it appears instantly

### **3. Advanced Search:**
- Navigate to Programs or Applications
- Apply filters
- Save search
- Verify URL updates

### **4. Calendar:**
- Navigate to `/calendar/`
- Verify events load
- Try different views
- Click event to navigate

### **5. Preferences:**
- Navigate to `/preferences/`
- Change settings
- Verify changes apply
- Reload page to verify persistence

---

## 🔄 **Rollback Plan**

If issues arise, you can disable features individually:

### **Disable WebSocket Notifications:**
```bash
FEATURE_WEBSOCKET_NOTIFICATIONS=False
```
Notifications will still work via API polling.

### **Disable Advanced Search:**
```bash
FEATURE_ADVANCED_SEARCH=False
```
Basic search will still work.

### **Disable Calendar:**
```bash
FEATURE_CALENDAR_VIEW=False
```
Date information still available in list views.

### **Disable Notification Center:**
```bash
FEATURE_NOTIFICATION_CENTER=False
```
Notifications still sent via email.

### **Complete Rollback:**

If you need to completely revert:

```bash
# Revert to previous version
git revert <commit-hash>

# Or checkout previous commit
git checkout <previous-commit>

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🎊 **Deployment Complete!**

Once all steps are complete, you'll have:
- ✅ Real-time WebSocket notifications
- ✅ Full notification center
- ✅ Advanced search with saved searches
- ✅ Calendar integration
- ✅ Reminder system
- ✅ Accessibility features
- ✅ Dark mode support

**Congratulations! Phase 2 Critical Features are now live!** 🎉

