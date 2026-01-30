"""CMS app configuration."""

from django.apps import AppConfig


class CmsConfig(AppConfig):
    """Configuration for the CMS app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms'
    verbose_name = 'Content Management System'

