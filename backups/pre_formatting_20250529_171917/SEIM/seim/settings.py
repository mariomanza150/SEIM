"""
Django settings for seim project.

This file determines which settings file to use based on the DJANGO_ENV
environment variable. It defaults to development settings.
"""

import os
from pathlib import Path

# Determine which settings to use
env = os.environ.get('DJANGO_ENV', 'dev')

if env == 'production' or env == 'prod':
    from .custom_settings.prod import *
elif env == 'development' or env == 'dev':
    from .custom_settings.dev import *
else:
    from .custom_settings.base import *

# You can override any settings here if needed
# For example, to ensure certain settings are always applied:

# Ensure the logs directory exists
logs_dir = Path(__file__).resolve().parent.parent / 'logs'
logs_dir.mkdir(exist_ok=True)

# Ensure the media directory exists
media_dir = Path(__file__).resolve().parent.parent / 'media'
media_dir.mkdir(exist_ok=True)
