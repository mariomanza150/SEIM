Notifications Module
===================

The notifications module handles email and in-app notifications in SEIM.

Overview
--------

The notifications module provides:

* Email notification system
* Async email processing via Celery
* Notification templates and preferences
* Multiple email backend support (SMTP, AWS SES)
* In-app notification tracking
* Notification history and audit

Models
------

.. automodule:: notifications.models
   :members:
   :undoc-members:
   :show-inheritance:

Notification Model
-----------------

The Notification model represents in-app notifications:

.. autoclass:: notifications.models.Notification
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Notification Types**: Different types of notifications
* **User Targeting**: Notifications sent to specific users
* **Read Status**: Track whether notifications are read
* **Related Objects**: Link notifications to specific objects
* **Template Support**: Use notification templates

Example Usage:

.. code-block:: python

    from notifications.models import Notification, NotificationType
    
    # Create notification type
    notification_type = NotificationType.objects.create(
        name='application_submitted',
        description='Notification when application is submitted',
        email_template='notifications/email/application_submitted.html',
        subject_template='Application Submitted Successfully'
    )
    
    # Create notification
    notification = Notification.objects.create(
        user=student,
        notification_type=notification_type,
        title='Application Submitted',
        message='Your application for Erasmus+ has been submitted successfully.',
        related_object_type='Application',
        related_object_id=application.id
    )

NotificationType Model
---------------------

.. autoclass:: notifications.models.NotificationType
   :members:
   :undoc-members:
   :show-inheritance:

NotificationPreference Model
---------------------------

.. autoclass:: notifications.models.NotificationPreference
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: notifications.services
   :members:
   :undoc-members:
   :show-inheritance:

NotificationService
------------------

The NotificationService handles all notification operations:

.. autoclass:: notifications.services.NotificationService
   :members:
   :undoc-members:
   :show-inheritance:

Key Methods:

* **send_notification()**: Send notification to user
* **send_email_notification()**: Send email notification
* **send_bulk_notifications()**: Send notifications to multiple users
* **mark_as_read()**: Mark notification as read
* **get_user_notifications()**: Get notifications for user

Example Usage:

.. code-block:: python

    from notifications.services import NotificationService
    
    # Send simple notification
    NotificationService.send_notification(
        user=student,
        notification_type='application_submitted',
        title='Application Submitted',
        message='Your application has been submitted successfully.',
        related_object=application
    )
    
    # Send email notification
    NotificationService.send_email_notification(
        user=student,
        template_name='application_submitted',
        context={
            'application': application,
            'program': application.program
        }
    )
    
    # Send bulk notifications
    NotificationService.send_bulk_notifications(
        users=[coordinator1, coordinator2],
        notification_type='new_application',
        title='New Application Received',
        message='A new application requires review.',
        related_object=application
    )

EmailService
-----------

.. automodule:: notifications.services.EmailService
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: notifications.views
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: notifications.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: notifications.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: notifications.urls
   :members:
   :undoc-members:
   :show-inheritance:

Tasks
-----

.. automodule:: notifications.tasks
   :members:
   :undoc-members:
   :show-inheritance:

Notification Workflow
--------------------

The notification workflow follows these steps:

.. mermaid::

    flowchart TD
        A[Event Occurs] --> B[Create Notification]
        B --> C[Check User Preferences]
        C --> D{Email Enabled?}
        D -->|Yes| E[Queue Email Task]
        D -->|No| F[Store In-App Only]
        E --> G[Celery Processes Task]
        G --> H[Send Email]
        H --> I[Update Status]
        F --> I
        I --> J[User Receives Notification]

Email Configuration
------------------

SEIM supports multiple email backends:

**Development Configuration:**

.. code-block:: python

    # settings/development.py
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

**Production SMTP Configuration:**

.. code-block:: python

    # settings/production.py
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-app-password'

**AWS SES Configuration:**

.. code-block:: python

    # settings/production.py
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_ACCESS_KEY_ID = 'your-access-key'
    AWS_SES_SECRET_ACCESS_KEY = 'your-secret-key'
    AWS_SES_REGION_NAME = 'us-east-1'

Notification Templates
---------------------

Email notifications use Django templates:

**HTML Template Example:**

.. code-block:: html

    <!-- notifications/email/application_submitted.html -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Application Submitted</title>
    </head>
    <body>
        <h2>Application Submitted Successfully</h2>
        <p>Dear {{ user.first_name }},</p>
        <p>Your application for <strong>{{ application.program.name }}</strong> has been submitted successfully.</p>
        <p>Application Details:</p>
        <ul>
            <li>Program: {{ application.program.name }}</li>
            <li>Submitted: {{ application.submitted_at|date:"F j, Y" }}</li>
            <li>Status: {{ application.status.name|title }}</li>
        </ul>
        <p>You will be notified when your application is reviewed.</p>
        <p>Best regards,<br>SEIM Team</p>
    </body>
    </html>

**Text Template Example:**

.. code-block:: text

    Application Submitted Successfully
    
    Dear {{ user.first_name }},
    
    Your application for {{ application.program.name }} has been submitted successfully.
    
    Application Details:
    - Program: {{ application.program.name }}
    - Submitted: {{ application.submitted_at|date:"F j, Y" }}
    - Status: {{ application.status.name|title }}
    
    You will be notified when your application is reviewed.
    
    Best regards,
    SEIM Team

Notification Types
-----------------

SEIM includes several built-in notification types:

* **application_submitted**: When student submits application
* **application_status_change**: When application status changes
* **document_uploaded**: When document is uploaded
* **document_resubmission_requested**: When resubmission is requested
* **comment_added**: When comment is added to application
* **password_reset**: When password reset is requested
* **email_verification**: When email verification is sent

Example Notification Type Configuration:

.. code-block:: python

    # Create notification types
    notification_types = [
        {
            'name': 'application_submitted',
            'description': 'Notification when application is submitted',
            'email_template': 'notifications/email/application_submitted.html',
            'subject_template': 'Application Submitted Successfully',
            'default_enabled': True
        },
        {
            'name': 'application_status_change',
            'description': 'Notification when application status changes',
            'email_template': 'notifications/email/status_change.html',
            'subject_template': 'Application Status Updated',
            'default_enabled': True
        },
        {
            'name': 'document_resubmission_requested',
            'description': 'Notification when document resubmission is requested',
            'email_template': 'notifications/email/resubmission_requested.html',
            'subject_template': 'Document Resubmission Required',
            'default_enabled': True
        }
    ]

Celery Integration
-----------------

Notifications use Celery for async processing:

.. code-block:: python

    # notifications/tasks.py
    from celery import shared_task
    from .services import NotificationService
    
    @shared_task
    def send_email_notification_task(user_id, template_name, context):
        """Send email notification asynchronously."""
        from accounts.models import User
        user = User.objects.get(id=user_id)
        
        NotificationService.send_email_notification(
            user=user,
            template_name=template_name,
            context=context
        )
    
    @shared_task
    def send_bulk_email_notifications_task(user_ids, template_name, context):
        """Send bulk email notifications asynchronously."""
        from accounts.models import User
        users = User.objects.filter(id__in=user_ids)
        
        for user in users:
            NotificationService.send_email_notification(
                user=user,
                template_name=template_name,
                context=context
            )

User Preferences
---------------

Users can configure their notification preferences:

.. code-block:: python

    from notifications.models import NotificationPreference
    
    # Get user preferences
    preferences = NotificationPreference.objects.get_or_create(
        user=user,
        notification_type=notification_type
    )[0]
    
    # Update preferences
    preferences.email_enabled = True
    preferences.in_app_enabled = True
    preferences.save()
    
    # Check if notification should be sent
    if preferences.email_enabled:
        NotificationService.send_email_notification(...)

Business Rules
-------------

* Notifications are sent for all critical workflow events
* Emails are sent asynchronously via Celery
* Failed email deliveries are logged but don't block workflows
* Users can configure notification preferences
* Notification history is preserved for audit purposes
* Email templates are customizable
* Support for HTML and plain text emails
* Rate limiting for email sending (100/min default)
* Notification preferences are user-specific

Related Documentation
--------------------

* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for notification management
* :doc:`exchange` - Application workflow integration
* :doc:`celery` - Background task processing 