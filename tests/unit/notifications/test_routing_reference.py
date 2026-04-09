"""Unit tests for ``notifications.routing_reference``."""

from notifications.routing_reference import (
    REMINDER_EVENT_TYPE_DESCRIPTIONS,
    REMINDER_EVENT_TYPE_RECIPIENT_SUMMARIES,
    SETTINGS_CATEGORY_PRIMARY_RECIPIENTS,
    TRANSACTIONAL_NOTIFICATION_ROUTES,
    UNGATED_SETTINGS_CATEGORY_BUCKET,
    build_notification_routing_reference,
)
from notifications.services import SETTINGS_CATEGORY_USER_FIELDS
from notifications.tasks import REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY


def test_build_notification_routing_reference_shape():
    data = build_notification_routing_reference()
    assert data["schema_version"] == 11
    access = data["reference_api_access"]
    assert access["superuser"] is True
    assert "coordinator" in access["roles_any"]
    assert "403" in access["description"]
    cats = data["settings_categories"]
    assert "applications" in cats
    assert cats["applications"]["email_user_settings_field"] == "email_applications"
    assert cats["applications"]["inapp_user_settings_field"] == "inapp_applications"
    assert "typical_triggers" in cats["applications"]
    assert "Application lifecycle" in cats["applications"]["typical_triggers"]
    assert "applicant" in cats["applications"]["primary_recipients"].lower()
    assert "system" in cats
    assert "notes" in cats["system"]
    assert data["reminder_default_settings_category"] == "programs"
    assert "application_deadline" in data["reminder_event_type_to_settings_category"]
    rdesc = data["reminder_event_type_descriptions"]
    assert rdesc["application_deadline"]
    assert "Legacy" in rdesc["application"]
    rrec = data["reminder_event_type_recipient_summaries"]
    assert rrec.keys() == rdesc.keys()
    assert "Reminder.user" in rrec["application_deadline"]
    digest = data["digest"]
    assert digest["settings_category"] == "system"
    assert "email_system" in digest["email_gates"]
    assert "Scheduled job" in digest["typical_triggers"]
    assert "Each user individually" in digest["recipient_summary"]
    routes = data["transactional_routes"]
    assert len(routes) == len(TRANSACTIONAL_NOTIFICATION_ROUTES)
    keys = [r["route_key"] for r in routes]
    assert keys == sorted(keys)
    assert keys == sorted({k["route_key"] for k in TRANSACTIONAL_NOTIFICATION_ROUTES})
    tx_idx = data["transactional_route_keys_by_settings_category"]
    assert UNGATED_SETTINGS_CATEGORY_BUCKET in tx_idx
    assert "applications" in tx_idx
    assert "application_submitted" in tx_idx["applications"]
    assert sum(len(v) for v in tx_idx.values()) == len(TRANSACTIONAL_NOTIFICATION_ROUTES)


def test_reminder_event_types_have_descriptions():
    for key in REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY:
        assert key in REMINDER_EVENT_TYPE_DESCRIPTIONS
        assert REMINDER_EVENT_TYPE_DESCRIPTIONS[key].strip()


def test_reminder_event_types_have_recipient_summaries():
    for key in REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY:
        assert key in REMINDER_EVENT_TYPE_RECIPIENT_SUMMARIES
        assert REMINDER_EVENT_TYPE_RECIPIENT_SUMMARIES[key].strip()


def test_settings_category_primary_recipients_complete():
    for key in SETTINGS_CATEGORY_USER_FIELDS:
        assert key in SETTINGS_CATEGORY_PRIMARY_RECIPIENTS
        assert SETTINGS_CATEGORY_PRIMARY_RECIPIENTS[key].strip()
    assert "system" in SETTINGS_CATEGORY_PRIMARY_RECIPIENTS


def test_build_includes_primary_recipients_on_each_category():
    cats = build_notification_routing_reference()["settings_categories"]
    for key, row in cats.items():
        assert "primary_recipients" in row
        assert row["primary_recipients"].strip()


def test_transactional_routes_settings_categories_valid():
    allowed = frozenset(SETTINGS_CATEGORY_USER_FIELDS) | {"system"}
    for row in build_notification_routing_reference()["transactional_routes"]:
        cat = row.get("settings_category")
        if cat is not None:
            assert cat in allowed
        assert row["route_key"].strip()
        assert row["summary"].strip()
        assert row["source"].strip()
        assert str(row["recipient_summary"]).strip()
