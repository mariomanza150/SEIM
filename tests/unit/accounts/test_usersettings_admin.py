"""UserSettings Django admin — notification routing discoverability."""

from django.contrib import admin

from accounts.admin import UserSettingsAdmin
from accounts.models import UserSettings


def test_notification_routing_documentation_html():
    ma = UserSettingsAdmin(UserSettings, admin.site)
    html = ma.notification_routing_documentation(None)
    content = str(html)
    assert "/seim/notification-routing" in content
    assert "/api/docs/" in content
    assert 'rel="noopener noreferrer"' in content


def test_usersettings_admin_readonly_includes_documentation():
    ma = UserSettingsAdmin(UserSettings, admin.site)
    assert "notification_routing_documentation" in ma.readonly_fields
