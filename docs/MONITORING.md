# Monitoring Guide

This guide covers monitoring strategies for the SEIM application in development and production environments.

## Overview

Effective monitoring helps:
- Detect issues before users report them
- Understand application performance
- Track usage patterns
- Ensure system reliability
- Plan for scaling

## Application Monitoring

### 1. Error Tracking (Sentry)

#### Setup
```python
# requirements.txt
sentry-sdk==1.5.12

# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    send_default_pii=True
)
```

#### Custom Error Logging
```python
# In your code
import sentry_sdk

try:
    process_exchange(exchange_id)
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise

# Add context
with sentry_sdk.configure_scope() as scope:
    scope.set_context("exchange", {
        "id": exchange.id,
        "status": exchange.status,
        "student": exchange.student.email
    })
```

### 2. Performance Monitoring

#### Django Debug Toolbar (Development)
```python
# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

#### New Relic (Production)
```python
# requirements.txt
newrelic==6.4.0

# Procfile or startup script
web: newrelic-admin run-program gunicorn seim.wsgi
```

#### Custom Metrics
```python
# metrics.py
import time
from functools import wraps

def track_time(metric_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            # Send to monitoring service
            send_metric(f"{metric_name}.duration", duration)
            return result
        return wrapper
    return decorator

# Usage
@track_time('exchange.approval')
def approve_exchange(exchange_id):
    # Implementation
```

### 3. Application Logging

#### Configuration
```python
# settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/seim/app.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'exchange': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### Usage
```python
import logging

logger = logging.getLogger('exchange')

def process_application(exchange_id):
    logger.info(f"Processing exchange {exchange_id}")
    try:
        # Processing logic
        logger.debug(f"Exchange {exchange_id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing exchange {exchange_id}: {e}", exc_info=True)
        raise
```

## Infrastructure Monitoring

### 1. Server Metrics

#### Prometheus + Grafana
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  node_exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro

volumes:
  prometheus_data:
  grafana_data:
```

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'django'
    static_configs:
      - targets: ['web:8000']
```

### 2. Database Monitoring

#### PostgreSQL Metrics
```python
# monitoring/db_metrics.py
from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Active connections
            cursor.execute("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active';
            """)
            active_connections = cursor.fetchone()[0]
            
            # Database size
            cursor.execute("""
                SELECT pg_database_size(current_database());
            """)
            db_size = cursor.fetchone()[0]
            
            # Slow queries
            cursor.execute("""
                SELECT query, calls, mean_exec_time
                FROM pg_stat_statements
                WHERE mean_exec_time > 100
                ORDER BY mean_exec_time DESC
                LIMIT 10;
            """)
            slow_queries = cursor.fetchall()
            
            # Send to monitoring service
            send_metric('db.connections.active', active_connections)
            send_metric('db.size', db_size)
```

#### pgBadger for PostgreSQL Analysis
```bash
# Install pgBadger
apt-get install pgbadger

# Generate report
pgbadger /var/log/postgresql/postgresql.log -o report.html
```

### 3. Application Metrics

#### Django Prometheus Integration
```python
# requirements.txt
django-prometheus==2.2.0

# settings/production.py
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
urlpatterns += [path('', include('django_prometheus.urls'))]
```

#### Custom Business Metrics
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
exchange_created = Counter(
    'seim_exchange_created_total',
    'Total number of exchanges created',
    ['status']
)

processing_time = Histogram(
    'seim_exchange_processing_seconds',
    'Time spent processing exchanges'
)

active_exchanges = Gauge(
    'seim_active_exchanges',
    'Number of active exchanges',
    ['status']
)

# Use in views/services
def create_exchange(request):
    # ... create exchange logic
    exchange_created.labels(status='draft').inc()
    
@processing_time.time()
def process_exchange(exchange_id):
    # ... processing logic
    
def update_active_exchanges():
    for status in Exchange.STATUS_CHOICES:
        count = Exchange.objects.filter(status=status[0]).count()
        active_exchanges.labels(status=status[0]).set(count)
```

## Real-time Monitoring

### 1. Health Checks

#### Django Health Check
```python
# requirements.txt
django-health-check==3.16.4

# settings/base.py
INSTALLED_APPS += [
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

# urls.py
urlpatterns += [path('health/', include('health_check.urls'))]
```

#### Custom Health Checks
```python
# monitoring/health_checks.py
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException

class DatabaseConnectionHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            raise HealthCheckException(f"Database error: {e}")

class FileStorageHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        try:
            from django.core.files.storage import default_storage
            default_storage.exists('health_check.txt')
        except Exception as e:
            raise HealthCheckException(f"Storage error: {e}")
```

### 2. Real-time Dashboards

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "SEIM Monitoring",
    "panels": [
      {
        "title": "Exchange Creation Rate",
        "targets": [
          {
            "expr": "rate(seim_exchange_created_total[5m])"
          }
        ]
      },
      {
        "title": "API Response Times",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket[5m])) by (view, le))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(django_http_responses_total_by_status{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

## Alert Configuration

### 1. Prometheus Alerts

```yaml
# alerts.yml
groups:
  - name: seim_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(django_http_responses_total_by_status{status=~"5.."}[5m]) > 0.05
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: DatabaseConnectionHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "{{ $value }} active connections"
      
      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Only {{ $value | humanizePercentage }} disk space remaining"
```

### 2. Alert Routing

```yaml
# alertmanager.yml
global:
  smtp_from: 'alerts@seim-project.org'
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'alerts@seim-project.org'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname', 'severity']
  receiver: 'team-emails'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'team-emails'
    email_configs:
      - to: 'dev-team@seim-project.org'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
  
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
```

## Log Management

### 1. Centralized Logging (ELK Stack)

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  es_data:
```

#### Logstash Configuration
```ruby
# logstash.conf
input {
  file {
    path => "/var/log/seim/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  if [logger_name] == "django.request" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "seim-%{+YYYY.MM.dd}"
  }
}
```

### 2. Structured Logging

```python
# settings/production.py
LOGGING = {
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/seim/app.json',
            'formatter': 'json',
        }
    }
}

# Usage
import structlog

logger = structlog.get_logger()

logger.info(
    "exchange_processed",
    exchange_id=exchange.id,
    status=exchange.status,
    processing_time=0.123,
    user_id=request.user.id
)
```

## Performance Monitoring

### 1. APM Integration

#### DataDog APM
```python
# requirements.txt
ddtrace==0.54.0

# Dockerfile
RUN pip install ddtrace

# Run with tracing
CMD ["ddtrace-run", "gunicorn", "seim.wsgi:application"]

# settings/production.py
DATADOG_TRACE = {
    'AGENT_HOSTNAME': 'datadog-agent',
    'AGENT_PORT': 8126,
}
```

### 2. Database Query Monitoring

```python
# monitoring/db_monitor.py
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger('monitoring')

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Monitor slow queries
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT query, calls, mean_exec_time, max_exec_time
                FROM pg_stat_statements
                WHERE mean_exec_time > 100
                ORDER BY mean_exec_time DESC
                LIMIT 20;
            """)
            
            for query in cursor.fetchall():
                logger.warning(
                    "slow_query",
                    query=query[0],
                    calls=query[1],
                    mean_time=query[2],
                    max_time=query[3]
                )
```

## Security Monitoring

### 1. Failed Login Attempts

```python
# monitoring/security.py
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_failed_login(sender, credentials, **kwargs):
    logger.warning(
        "failed_login_attempt",
        username=credentials.get('username'),
        ip_address=get_client_ip(kwargs.get('request'))
    )
```

### 2. Suspicious Activity Detection

```python
# monitoring/activity_monitor.py
from django.core.cache import cache
from datetime import datetime, timedelta

class ActivityMonitor:
    def check_rate_limit(self, user_id, action, limit=100, window=3600):
        key = f"rate_limit:{user_id}:{action}"
        count = cache.get(key, 0)
        
        if count >= limit:
            logger.warning(
                "rate_limit_exceeded",
                user_id=user_id,
                action=action,
                count=count
            )
            return False
        
        cache.set(key, count + 1, window)
        return True
    
    def detect_anomalies(self, user_id):
        # Check for unusual patterns
        recent_actions = self.get_recent_actions(user_id)
        
        # Multiple failed logins
        failed_logins = [a for a in recent_actions if a.type == 'login_failed']
        if len(failed_logins) > 5:
            self.alert_security_team(user_id, "Multiple failed login attempts")
        
        # Unusual download patterns
        downloads = [a for a in recent_actions if a.type == 'document_download']
        if len(downloads) > 50:
            self.alert_security_team(user_id, "Excessive downloads")
```

## Monitoring Best Practices

### 1. Set Meaningful Alerts
- Alert on symptoms, not causes
- Set appropriate thresholds
- Avoid alert fatigue
- Include context in alerts

### 2. Dashboard Design
- One dashboard per service/team
- Key metrics above the fold
- Use consistent color schemes
- Include relevant time ranges

### 3. Log Retention Policy
```python
# settings/production.py
LOG_RETENTION_DAYS = {
    'application': 30,
    'access': 90,
    'error': 180,
    'security': 365,
}
```

### 4. Regular Reviews
- Weekly metrics review
- Monthly trend analysis
- Quarterly capacity planning
- Annual architecture review

## Monitoring Checklist

### Development
- [ ] Local logging configured
- [ ] Debug toolbar installed
- [ ] Performance profiling tools
- [ ] Test monitoring setup

### Staging
- [ ] Metrics collection enabled
- [ ] Alert rules configured
- [ ] Dashboard created
- [ ] Log aggregation setup

### Production
- [ ] Error tracking (Sentry)
- [ ] APM configured
- [ ] Health checks enabled
- [ ] Security monitoring active
- [ ] Backup monitoring
- [ ] SSL certificate monitoring
- [ ] Uptime monitoring
- [ ] Capacity alerts

## Useful Commands

### View Logs
```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# Nginx logs
docker-compose logs -f nginx

# Filter logs
docker-compose logs web | grep ERROR

# Save logs
docker-compose logs > logs.txt
```

### Metrics Collection
```bash
# Export Prometheus metrics
curl http://localhost:8000/metrics

# Check health status
curl http://localhost:8000/health/

# Database statistics
docker-compose exec db psql -U seim_user -c "SELECT * FROM pg_stat_activity;"
```

This monitoring guide provides comprehensive coverage of application, infrastructure, and security monitoring for the SEIM project. Regular monitoring and alerting help maintain system reliability and performance.
