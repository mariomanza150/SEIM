"""Unit tests for ``notifications.routing_reference``."""

from notifications.routing_reference import build_notification_routing_reference


def test_build_notification_routing_reference_shape():
    data = build_notification_routing_reference()
    assert data["schema_version"] == 1
    cats = data["settings_categories"]
    assert "applications" in cats
    assert cats["applications"]["email_user_settings_field"] == "email_applications"
    assert cats["applications"]["inapp_user_settings_field"] == "inapp_applications"
    assert "system" in cats
    assert "notes" in cats["system"]
    assert data["reminder_default_settings_category"] == "programs"
    assert "application_deadline" in data["reminder_event_type_to_settings_category"]
    digest = data["digest"]
    assert digest["settings_category"] == "system"
    assert "email_system" in digest["email_gates"]
