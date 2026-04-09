"""
Wagtail-enabled test settings for CMS unit tests.

`seim.settings.test` removes Wagtail and `cms` for speed. Tests under
`tests/unit/cms/` that import Wagtail models must set::

    DJANGO_SETTINGS_MODULE=seim.settings.test_cms

(Still uses in-memory SQLite when ``DATABASE_URL`` is unset, same as ``test``.)
"""

import copy

from .base import INSTALLED_APPS as _BASE_INSTALLED_APPS
from .base import TEMPLATES as _BASE_TEMPLATES
from .test import *  # noqa: F403, F401

INSTALLED_APPS = [app for app in _BASE_INSTALLED_APPS if app != "cacheops"]

TEMPLATES = copy.deepcopy(_BASE_TEMPLATES)

MIDDLEWARE = list(MIDDLEWARE)
_wagtail_redirect = "wagtail.contrib.redirects.middleware.RedirectMiddleware"
if _wagtail_redirect not in MIDDLEWARE:
    _insert_at = next(
        i
        for i, m in enumerate(MIDDLEWARE)
        if m.endswith("XFrameOptionsMiddleware")
    )
    MIDDLEWARE.insert(_insert_at, _wagtail_redirect)
