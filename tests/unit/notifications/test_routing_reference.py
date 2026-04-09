"""Unit tests for ``notifications.routing_reference``."""

from notifications.routing_reference import (
    REMINDER_EVENT_TYPE_DESCRIPTIONS,
    build_notification_routing_reference,
)
from notifications.tasks import REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY


def test_build_notification_routing_reference_shape():
    data = build_notification_routing_reference()
    assert data["schema_version"] == 4
    cats = data["settings_categories"]
    assert "applications" in cats
    assert cats["applications"]["email_user_settings_field"] == "email_applications"
    assert cats["applications"]["inapp_user_settings_field"] == "inapp_applications"
    assert "typical_triggers" in cats["applications"]
    assert "Application lifecycle" in cats["applications"]["typical_triggers"]
    assert "system" in cats
    assert "notes" in cats["system"]
    assert data["reminder_default_settings_category"] == "programs"
    assert "application_deadline" in data["reminder_event_type_to_settings_category"]
    rdesc = data["reminder_event_type_descriptions"]
    assert rdesc["application_deadline"]
    assert "Legacy" in rdesc["application"]
    digest = data["digest"]
    assert digest["settings_category"] == "system"
    assert "email_system" in digest["email_gates"]
    assert "Scheduled job" in digest["typical_triggers"]


def test_reminder_event_types_have_descriptions():
    for key in REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY:
        assert key in REMINDER_EVENT_TYPE_DESCRIPTIONS
        assert REMINDER_EVENT_TYPE_DESCRIPTIONS[key].strip()
