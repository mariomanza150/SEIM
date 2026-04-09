"""
CMS Admin Configuration

Wagtail admin customization.
"""

from django.contrib import admin


# Add a custom admin site header
admin.site.site_header = "SEIM Administration"
admin.site.site_title = "SEIM Admin"
admin.site.index_title = "Welcome to SEIM Administration"
