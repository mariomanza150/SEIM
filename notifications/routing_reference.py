"""
Read-only description of how notification sends map to ``UserSettings`` fields.

Used by the staff API and kept in sync with ``NotificationService`` routing.
"""

from __future__ import annotations

from notifications.services import SETTINGS_CATEGORY_USER_FIELDS
from notifications.tasks import REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY

# Staff-facing text for each ``Reminder.event_type`` key in the routing map.
REMINDER_EVENT_TYPE_DESCRIPTIONS: dict[str, str] = {
    "application_deadline": (
        "Deadline reminder tied to an application milestone (e.g. submission or review cutoff)."
    ),
    "document_deadline": "Reminder for a required document due date.",
    "program_start": "Reminder anchored to the operational program start date.",
    "program_end": "Reminder anchored to the program end date.",
    "custom": (
        "User-defined reminder; delivery uses the programs notification group unless the "
        "event type is extended elsewhere."
    ),
    "application": "Legacy event_type value; uses the applications UserSettings group.",
    "document": "Legacy event_type value; uses the documents UserSettings group.",
    "program": "Legacy event_type value; uses the programs UserSettings group.",
}

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

DIGEST_TYPICAL_TRIGGERS = (
    "Scheduled job summarizes unread in-app notifications for users who enabled a digest "
    "frequency. Sends use settings_category=system: in-app delivery respects inapp_system; "
    "email requires email_system and email_notification_digest (and digest frequency not off)."
)

# Mirrors ``NotificationRoutingReferenceView`` permission rules (for staff UI + API clients).
REFERENCE_API_ACCESS: dict[str, object] = {
    "roles_any": ["coordinator", "admin"],
    "superuser": True,
    "description": (
        "GET /api/notifications/routing-reference/ returns this JSON only for authenticated "
        "users who are Django superuser or have the coordinator or admin role; others get HTTP 403."
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
    reminder_map = dict(REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY)
    return {
        "schema_version": 5,
        "reference_api_access": dict(REFERENCE_API_ACCESS),
        "settings_categories": categories,
        "reminder_event_type_to_settings_category": reminder_map,
        "reminder_event_type_descriptions": {
            k: REMINDER_EVENT_TYPE_DESCRIPTIONS[k] for k in reminder_map
        },
        "reminder_default_settings_category": "programs",
        "digest": {
            "settings_category": "system",
            "email_gates": ["email_system", "email_notification_digest"],
            "inapp_user_settings_field": "inapp_system",
            "typical_triggers": DIGEST_TYPICAL_TRIGGERS,
        },
    }
