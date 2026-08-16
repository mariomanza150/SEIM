Core Module
==========

The core module provides shared utilities, base models, and common functionality used across SEIM.

Overview
--------

The core module provides:

* Base models and mixins
* Common utilities and helpers
* Shared configuration
* Cache management
* Background task configuration
* Common permissions and decorators

Models
------

.. automodule:: core.models
   :members:
   :undoc-members:
   :show-inheritance:

TimeStampedModel
----------------

The TimeStampedModel provides automatic timestamp fields:

.. autoclass:: core.models.TimeStampedModel
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Automatic Timestamps**: Created and updated timestamps
* **Django Integration**: Uses Django's auto_now and auto_now_add
* **Audit Trail**: Track when records are created and modified
* **Consistent Interface**: Standard interface across all models

Example Usage:

.. code-block:: python

    from core.models import TimeStampedModel
    from django.db import models
    
    class MyModel(TimeStampedModel):
        name = models.CharField(max_length=100)
        description = models.TextField()
        
        def __str__(self):
            return self.name
    
    # Create instance
    instance = MyModel.objects.create(
        name='Test Model',
        description='A test model with timestamps'
    )
    
    # Timestamps are automatically set
    print(f"Created: {instance.created_at}")
    print(f"Updated: {instance.updated_at}")
    
    # Update instance
    instance.name = 'Updated Test Model'
    instance.save()
    
    # Updated timestamp is automatically updated
    print(f"Updated: {instance.updated_at}")

UUIDModel
---------

The UUIDModel provides UUID primary keys:

.. autoclass:: core.models.UUIDModel
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **UUID Primary Keys**: Secure, non-sequential primary keys
* **Global Uniqueness**: UUIDs are globally unique
* **Security**: No predictable ID sequences
* **Distributed Systems**: Suitable for distributed architectures

Example Usage:

.. code-block:: python

    from core.models import UUIDModel
    from django.db import models
    
    class SecureModel(UUIDModel):
        name = models.CharField(max_length=100)
        
        def __str__(self):
            return self.name
    
    # Create instance
    instance = SecureModel.objects.create(name='Secure Model')
    
    # UUID is automatically generated
    print(f"ID: {instance.id}")  # e.g., "550e8400-e29b-41d4-a716-446655440000"

Services
--------

.. automodule:: core.services
   :members:
   :undoc-members:
   :show-inheritance:

Cache Management
---------------

The core module provides advanced cache management:

.. automodule:: core.cache
   :members:
   :undoc-members:
   :show-inheritance:

CacheManager
-----------

The CacheManager handles all caching operations:

.. autoclass:: core.cache.CacheManager
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Multi-tier Caching**: Different cache backends for different purposes
* **Cache Decorators**: Easy-to-use caching decorators
* **Cache Invalidation**: Pattern-based cache invalidation
* **Performance Monitoring**: Cache hit rate tracking
* **Compression**: Automatic data compression for large responses

Example Usage:

.. code-block:: python

    from core.cache import CacheManager, cache_api_response
    
    # Use cache decorator
    @cache_api_response(timeout=300)  # Cache for 5 minutes
    def get_program_list(request):
        return Program.objects.filter(is_active=True)
    
    # Manual cache operations
    cache_manager = CacheManager()
    
    # Set cache
    cache_manager.set('user_data', user_data, timeout=600)
    
    # Get cache
    cached_data = cache_manager.get('user_data')
    
    # Invalidate cache
    cache_manager.invalidate_pattern('api:ProgramViewSet:*')

Cache Decorators
----------------

SEIM provides several cache decorators:

.. code-block:: python

    from core.cache import cache_api_response, cache_user_data, cache_analytics
    
    # Cache API responses
    @cache_api_response(timeout=300)
    def api_view(request):
        return Response(data)
    
    # Cache user-specific data
    @cache_user_data(timeout=600)
    def user_dashboard(request):
        return user_data
    
    # Cache analytics data
    @cache_analytics(timeout=1800)
    def get_dashboard_metrics():
        return metrics

Celery Configuration
-------------------

The core module provides Celery configuration:

.. automodule:: core.celery
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Task Routing**: Route tasks to specific queues
* **Rate Limiting**: Prevent system overload
* **Memory Management**: Worker restart policies
* **Performance Monitoring**: Task performance tracking
* **Health Checks**: System health monitoring

Example Configuration:

.. code-block:: python

    # core/celery.py
    from celery import Celery
    from django.conf import settings
    
    app = Celery('seim')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Task routing
    app.conf.task_routes = {
        'notifications.tasks.*': {'queue': 'notifications'},
        'analytics.tasks.*': {'queue': 'analytics'},
        'documents.tasks.*': {'queue': 'documents'},
    }
    
    # Rate limiting
    app.conf.task_annotations = {
        'notifications.tasks.send_email': {'rate_limit': '100/m'},
        'analytics.tasks.generate_report': {'rate_limit': '10/m'},
    }
    
    # Memory management
    app.conf.worker_max_memory_per_child = 200000  # 200MB
    app.conf.worker_max_tasks_per_child = 1000

Utilities
---------

.. automodule:: core.utils
   :members:
   :undoc-members:
   :show-inheritance:

Common Utilities
---------------

SEIM provides various utility functions:

.. code-block:: python

    from core.utils import generate_uuid, validate_email, format_file_size
    
    # Generate UUID
    uuid = generate_uuid()
    
    # Validate email
    is_valid = validate_email('user@example.com')
    
    # Format file size
    formatted_size = format_file_size(1048576)  # "1.0 MB"

Permissions
-----------

.. automodule:: core.permissions
   :members:
   :undoc-members:
   :show-inheritance:

Custom Permissions
-----------------

SEIM provides custom permission classes:

.. code-block:: python

    from core.permissions import IsOwner, HasRole, IsCoordinator
    
    # Check if user owns the object
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [IsOwner]
    
    # Check if user has specific role
    class AdminViewSet(viewsets.ModelViewSet):
        permission_classes = [HasRole('admin')]
    
    # Check if user is coordinator
    class CoordinatorViewSet(viewsets.ModelViewSet):
        permission_classes = [IsCoordinator]

Management Commands
------------------

.. automodule:: core.management.commands
   :members:
   :undoc-members:
   :show-inheritance:

Available Commands
-----------------

SEIM provides several management commands:

.. code-block:: bash

    # Generate documentation
    python manage.py generate_docs --format yaml
    python manage.py generate_docs --include-code
    python manage.py generate_docs --include-db
    
    # Enhance docstrings
    python manage.py enhance_docstrings --force
    
    # Test cache
    python manage.py test_cache
    
    # Create initial data
    python manage.py create_initial_data

Configuration
-------------

The core module provides shared configuration:

.. code-block:: python

    # settings/base.py
    from core.config import *
    
    # Cache configuration
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'seim',
            'TIMEOUT': 300,
        },
    }
    
    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = True

Error Handling
-------------

The core module provides centralized error handling:

.. code-block:: python

    from core.exceptions import SEIMException, ValidationError
    
    # Custom exceptions
    class ApplicationError(SEIMException):
        """Base exception for application errors."""
        pass
    
    class DocumentValidationError(ValidationError):
        """Exception for document validation errors."""
        pass
    
    # Error handling
    try:
        # Some operation
        pass
    except ApplicationError as e:
        logger.error(f"Application error: {e}")
        return Response({'error': str(e)}, status=400)

Logging
-------

The core module provides centralized logging:

.. code-block:: python

    # settings/base.py
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': 'logs/seim.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'seim': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

Security
--------

The core module provides security utilities:

.. code-block:: python

    from core.security import sanitize_filename, validate_file_type
    
    # Sanitize filename
    safe_filename = sanitize_filename('my file (1).pdf')
    # Result: "my_file_1.pdf"
    
    # Validate file type
    is_valid = validate_file_type('document.pdf', ['pdf', 'doc', 'docx'])

Business Rules
-------------

* All models should inherit from TimeStampedModel for audit trails
* UUID models should be used for security-sensitive data
* Cache should be used for frequently accessed data
* Background tasks should use Celery for async processing
* All operations should be logged for audit purposes
* Error handling should be consistent across the application
* Security utilities should be used for file operations
* Configuration should be environment-specific

Related Documentation
--------------------

* :doc:`architecture` - System architecture overview
* :doc:`caching` - Cache management and optimization
* :doc:`celery` - Background task processing
* :doc:`security` - Security best practices
* :doc:`deployment` - Production deployment configuration 