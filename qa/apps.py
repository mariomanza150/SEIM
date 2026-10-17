from django.apps import AppConfig


class QaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "qa"
    verbose_name = "QA / Tester toolkit"

    def ready(self):
        from . import checks  # noqa: F401  (registers system checks)
