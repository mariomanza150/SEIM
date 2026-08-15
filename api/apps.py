"""Django app config for the REST API gateway (URL aggregator, no models)."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "SEIM REST API"
