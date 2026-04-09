"""Backward-compatible Celery entry point. The canonical app is ``seim.celery``."""

from seim.celery import app

__all__ = ("app",)
