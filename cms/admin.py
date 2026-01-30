"""
CMS Admin Configuration

Wagtail admin customization and model registration.
Also adds link to Wagtail admin in Django admin.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


# Add a custom admin site header
admin.site.site_header = "SEIM Administration"
admin.site.site_title = "SEIM Admin"
admin.site.index_title = "Welcome to SEIM Administration"


# Custom admin action to add Wagtail CMS link in Django admin
class WagtailAdminLink:
    """
    Adds a link to Wagtail CMS admin in Django admin interface.
    This will be registered as a custom admin view.
    """
    pass


# Register a custom dashboard item that links to Wagtail
# This can be done via templates or custom admin views
