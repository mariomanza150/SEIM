from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Celery autodiscover runs while seim.celery is imported (via seim/__init__.py),
        # often before apps are populated, so shared_task modules are skipped. Import
        # them here so workers and the beat scheduler see the real task list.
        for name in settings.INSTALLED_APPS:
            try:
                import_module(f"{name}.tasks")
            except ModuleNotFoundError:
                pass
