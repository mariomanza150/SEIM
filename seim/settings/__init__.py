"""
Settings package for SEIM project.

This package contains environment-specific settings files:
- base.py: Common settings shared across all environments
- development.py: Development-specific settings
- production.py: Production-specific settings

To use a specific settings file, set the DJANGO_SETTINGS_MODULE environment variable:
- Development: DJANGO_SETTINGS_MODULE=seim.settings.development
- Production: DJANGO_SETTINGS_MODULE=seim.settings.production
"""

# Default to development settings if not specified
import os

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.development")
