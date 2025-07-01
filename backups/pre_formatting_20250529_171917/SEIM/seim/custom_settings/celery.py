"""
Celery configuration for SGII application.
"""

import os
from celery.schedules import crontab

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Task serialization
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Task execution
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'False').lower() == 'true'
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Time zone
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task routing
CELERY_TASK_ROUTES = {
    'exchange.tasks.send_email': {'queue': 'email'},
    'exchange.tasks.generate_pdf': {'queue': 'documents'},
    'exchange.tasks.process_batch': {'queue': 'batch'},
    'exchange.tasks.update_analytics': {'queue': 'analytics'},
}

# Queue configuration
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

# Worker configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_WORKER_CONCURRENCY = None  # Use default (number of CPUs)

# Beat schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-sessions': {
        'task': 'exchange.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'send-reminder-emails': {
        'task': 'exchange.tasks.send_reminder_emails',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
    'update-exchange-analytics': {
        'task': 'exchange.tasks.update_analytics',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'cleanup-old-documents': {
        'task': 'exchange.tasks.cleanup_old_documents',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Run at 3 AM on Sundays
    },
}

# Task time limits
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes

# Result backend settings
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_PERSISTENT = True
CELERY_RESULT_COMPRESSION = 'gzip'

# Error handling
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_SEND_TASK_ERROR_EMAILS = True

# Monitoring
CELERY_SEND_EVENTS = True
CELERY_TASK_SEND_EVENTS = True

# Logging
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Redis specific settings
CELERY_REDIS_MAX_CONNECTIONS = 10
CELERY_REDIS_RETRY_ON_TIMEOUT = True
CELERY_REDIS_SOCKET_KEEPALIVE = True
