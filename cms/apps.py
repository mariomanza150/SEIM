"""CMS app configuration."""

from django.apps import AppConfig


class CmsConfig(AppConfig):
    """Configuration for the CMS app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms'
    verbose_name = 'Content Management System'

    def ready(self):
        """Apply fixes and initialize on app ready."""
        # Fix Wagtail rich text AssertionError: Unmatched tags: expected br, got p
        from cms.utils.richtext_fix import apply_richtext_fix
        apply_richtext_fix()
