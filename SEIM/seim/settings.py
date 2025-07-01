"""
Django settings for seim project.

This file determines which settings file to use based on the DJANGO_ENV
environment variable. It defaults to development settings.
"""

import os
from pathlib import Path

# Determine which settings to use
env = os.environ.get("DJANGO_ENV", "dev")

if env == "production" or env == "prod":
    from .custom_settings.prod import *
elif env == "development" or env == "dev":
    from .custom_settings.dev import *
else:
    from .custom_settings.base import *

# Dynamically import INSTALLED_APPS based on DJANGO_ENV
try:
    from .custom_settings.base import INSTALLED_APPS
except ImportError:
    INSTALLED_APPS = []

# Ensure the logs directory exists
logs_dir: Path = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Ensure the media directory exists
media_dir: Path = Path(__file__).resolve().parent.parent / "media"
media_dir.mkdir(exist_ok=True)

# Add ROOT_URLCONF for URL routing
ROOT_URLCONF = 'seim.urls'

# Django admin is already included in base settings
# No need to add it again here

# Verify template directories
from pathlib import Path
import os

def verify_template_dirs():
    from django.conf import settings
    for template_config in settings.TEMPLATES:
        if template_config['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
            for dir_path in template_config['DIRS']:
                if isinstance(dir_path, (str, Path)):
                    path = Path(dir_path)
                    if not path.exists():
                        print(f"Warning: Template directory does not exist: {path}")
                    else:
                        print(f"Template directory found: {path}")

# Call verification on startup
verify_template_dirs()
