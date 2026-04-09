"""
Read-only description of how notification sends map to ``UserSettings`` fields.

Used by the staff API and kept in sync with ``NotificationService`` routing.
"""

from __future__ import annotations

from notifications.services import SETTINGS_CATEGORY_USER_FIELDS
from notifications.tasks import REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY

# Short staff-facing hints: what transactional sends usually flow through each group.
SETTINGS_CATEGORY_TYPICAL_TRIGGERS: dict[str, str] = {
    "applications": (
        "Application lifecycle (submit, withdraw, status changes, waitlist) and "
        "coordinator/student signals tied to a specific application."
    ),
    "documents": (
        "Document upload/replace, validation outcomes, resubmission requests, and "
        "staff/student document feedback where delivery is grouped with document alerts."
    ),
    "comments": (
        "Comment threads on applications or documents (distinct from generic document alerts)."
    ),
    "programs": (
        "Program-related broadcasts and reminder event types mapped to the programs group "
        "(see reminder type → category table)."
    ),
    "system": (
        "Agreement expiration notices, scheduled notification digests, and similar "
        "institutional alerts. Digest email also requires email_notification_digest."
    ),
}


def build_notification_routing_reference() -> dict:
    """Structured map for coordinators/admins (API + future UI)."""
    categories = {
        key: {
            "email_user_settings_field": email_f,
            "inapp_user_settings_field": inapp_f,
            "typical_triggers": SETTINGS_CATEGORY_TYPICAL_TRIGGERS[key],
        }
        for key, (email_f, inapp_f) in SETTINGS_CATEGORY_USER_FIELDS.items()
    }
    categories["system"] = {
        "email_user_settings_field": "email_system",
        "inapp_user_settings_field": "inapp_system",
        "typical_triggers": SETTINGS_CATEGORY_TYPICAL_TRIGGERS["system"],
        "notes": (
            "Agreement expiration alerts, notification digests, and similar. "
            "For digest email, email_notification_digest must also be enabled."
        ),
    }
    return {
        "schema_version": 2,
        "settings_categories": categories,
        "reminder_event_type_to_settings_category": dict(
            REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY
        ),
        "reminder_default_settings_category": "programs",
        "digest": {
            "settings_category": "system",
            "email_gates": ["email_system", "email_notification_digest"],
            "inapp_user_settings_field": "inapp_system",
        },
    }
