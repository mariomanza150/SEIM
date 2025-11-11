from django.apps import AppConfig


class ApplicationFormsConfig(AppConfig):
    """
    Configuration for the Application Forms app.

    This app provides custom form type and submission tracking functionality
    that extends the official django-dynforms package. It stores form schemas
    and user responses, particularly for exchange program applications.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application_forms'
    verbose_name = 'Application Forms'

