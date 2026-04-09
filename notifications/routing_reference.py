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

# Who receives Celery deadline reminder notifications for each ``Reminder.event_type`` (always ``Reminder.user``).
REMINDER_EVENT_TYPE_RECIPIENT_SUMMARIES: dict[str, str] = {
    "application_deadline": (
        "The reminder owner (`Reminder.user`) — usually the student or staff who scheduled it."
    ),
    "document_deadline": (
        "The reminder owner (`Reminder.user`) — typically tracking a document due date."
    ),
    "program_start": "The reminder owner (`Reminder.user`).",
    "program_end": "The reminder owner (`Reminder.user`).",
    "custom": "The reminder owner (`Reminder.user`).",
    "application": "The reminder owner (`Reminder.user`); legacy `application` event type.",
    "document": "The reminder owner (`Reminder.user`); legacy `document` event type.",
    "program": "The reminder owner (`Reminder.user`); legacy `program` event type.",
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

# Who usually receives notifications gated by each group (high-level; actual routing is code-driven).
SETTINGS_CATEGORY_PRIMARY_RECIPIENTS: dict[str, str] = {
    "applications": (
        "Primarily the applicant; coordinators may receive parallel review or sync notices "
        "for the same application."
    ),
    "documents": (
        "The application student and/or document uploader; coordinators when staff actions "
        "generate student-facing document alerts."
    ),
    "comments": (
        "The other party on the thread (student ↔ coordinator/staff), depending on who authored "
        "the latest comment."
    ),
    "programs": (
        "Most often students for program announcements; reminder event types may target the "
        "reminder owner (see calendar/deadline features)."
    ),
    "system": (
        "Varies by alert: e.g. agreement expiration → staff; notification digest → each user "
        "who enabled digests and passes system gates."
    ),
}

DIGEST_TYPICAL_TRIGGERS = (
    "Scheduled job summarizes unread in-app notifications for users who enabled a digest "
    "frequency. Sends use settings_category=system: in-app delivery respects inapp_system; "
    "email requires email_system and email_notification_digest (and digest frequency not off)."
)

DIGEST_RECIPIENT_SUMMARY = (
    "Each user individually when the digest job selects them: digest frequency not off, they have "
    "unread in-app notifications to summarize, and at least one channel is allowed "
    "(in-app via inapp_system; email via email_system plus email_notification_digest)."
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

# Documented transactional sends that use ``settings_category`` (or intentionally omit it).
# Keep in sync with ``NotificationService.send_notification`` / bulk helpers in app code.
TRANSACTIONAL_NOTIFICATION_ROUTES: list[dict[str, object]] = [
    {
        "route_key": "account_security_email",
        "settings_category": None,
        "recipient_summary": "The affected end user only (email inbox).",
        "summary": (
            "Account lockout, email verification, password reset and change, registration welcome, "
            "deactivation — email-only flows that intentionally omit ``settings_category`` "
            "(not gated by notification-group toggles)."
        ),
        "source": "accounts.services.AccountService; accounts.views (resend verification)",
    },
    {
        "route_key": "agreement_expiration_alert",
        "settings_category": "system",
        "recipient_summary": (
            "Admins and coordinators (scoped to linked programs when configured; "
            "otherwise all coordinators)."
        ),
        "summary": (
            "Staff (admins / coordinators) notified when an agreement nears its end date; "
            "also subject to the agreement-expiration ``NotificationType`` preference when set."
        ),
        "source": "exchange.agreement_expiration",
    },
    {
        "route_key": "agreement_renewal_staff_bulk_in_app",
        "settings_category": None,
        "recipient_summary": "All users with admin or coordinator role (in-app list).",
        "summary": (
            "Bulk in-app notices to admins and coordinators for renewal workflow events; "
            "no ``settings_category`` (not filtered by UserSettings notification groups)."
        ),
        "source": "exchange.agreement_renewal._notify_staff",
    },
    {
        "route_key": "application_status_update",
        "settings_category": "applications",
        "recipient_summary": "The application student.",
        "summary": "Student notified when staff changes application status after submission.",
        "source": "exchange.services.ApplicationService.transition_status",
    },
    {
        "route_key": "application_submitted",
        "settings_category": "applications",
        "recipient_summary": "The applicant (student) who submitted.",
        "summary": "Student confirmation when a draft application is submitted successfully.",
        "source": "exchange.services.ApplicationService.submit_application",
    },
    {
        "route_key": "application_waitlist_received",
        "settings_category": "applications",
        "recipient_summary": "The applicant (student) placed on the waitlist.",
        "summary": "Student notified when submitted to a full program with waitlist enabled.",
        "source": "exchange.services.ApplicationService.submit_application",
    },
    {
        "route_key": "calendar_deadline_reminder",
        "settings_category": None,
        "recipient_summary": "The user who owns the reminder (same user as ``Reminder.user``).",
        "summary": (
            "Per-user calendar/deadline reminders; effective ``settings_category`` depends on "
            "``Reminder.event_type`` (see reminder_event_type_to_settings_category)."
        ),
        "source": "notifications.tasks.send_deadline_reminders",
    },
    {
        "route_key": "document_replaced_staff",
        "settings_category": "documents",
        "recipient_summary": (
            "Assigned application coordinator, else up to ten program coordinators (no duplicate sends per user)."
        ),
        "summary": (
            "Assigned coordinator or program coordinators notified when a student replaces "
            "a document file."
        ),
        "source": "documents.services.DocumentService.notify_coordinators_document_replaced",
    },
    {
        "route_key": "document_resubmission_requested",
        "settings_category": "documents",
        "recipient_summary": "The application student.",
        "summary": "Student notified when staff requests a document resubmission.",
        "source": "documents.services.DocumentService.request_resubmission",
    },
    {
        "route_key": "document_staff_comment_public",
        "settings_category": "comments",
        "recipient_summary": "The application student (document owner context).",
        "summary": "Student notified when staff adds a public comment on their document.",
        "source": "documents.serializers.DocumentCommentSerializer.create",
    },
    {
        "route_key": "document_validation_rejected",
        "settings_category": "documents",
        "recipient_summary": "The application student.",
        "summary": "Student notified when document validation result is invalid / not accepted.",
        "source": "documents.services.DocumentService.validate_document",
    },
    {
        "route_key": "notification_digest_unread_summary",
        "settings_category": "system",
        "recipient_summary": "Each recipient user individually (digest run per user).",
        "summary": (
            "Scheduled digest summarizing unread in-app notifications; respects system email/in-app "
            "gates and digest frequency."
        ),
        "source": "notifications.digest.process_notification_digests",
    },
]

# Bucket label when a transactional send omits ``settings_category`` (JSON object keys cannot be null).
UNGATED_SETTINGS_CATEGORY_BUCKET = "ungated"


def build_transactional_route_keys_by_settings_category() -> dict[str, list[str]]:
    """Group ``route_key`` values by ``settings_category`` for quick staff lookup."""
    buckets: dict[str, list[str]] = {}
    for row in TRANSACTIONAL_NOTIFICATION_ROUTES:
        raw_cat = row["settings_category"]
        label = raw_cat if raw_cat is not None else UNGATED_SETTINGS_CATEGORY_BUCKET
        buckets.setdefault(str(label), []).append(str(row["route_key"]))
    return {k: sorted(v) for k, v in sorted(buckets.items(), key=lambda kv: kv[0])}


def build_notification_routing_reference() -> dict:
    """Structured map for coordinators/admins (API + future UI)."""
    categories = {
        key: {
            "email_user_settings_field": email_f,
            "inapp_user_settings_field": inapp_f,
            "typical_triggers": SETTINGS_CATEGORY_TYPICAL_TRIGGERS[key],
            "primary_recipients": SETTINGS_CATEGORY_PRIMARY_RECIPIENTS[key],
        }
        for key, (email_f, inapp_f) in SETTINGS_CATEGORY_USER_FIELDS.items()
    }
    categories["system"] = {
        "email_user_settings_field": "email_system",
        "inapp_user_settings_field": "inapp_system",
        "typical_triggers": SETTINGS_CATEGORY_TYPICAL_TRIGGERS["system"],
        "primary_recipients": SETTINGS_CATEGORY_PRIMARY_RECIPIENTS["system"],
        "notes": (
            "Agreement expiration alerts, notification digests, and similar. "
            "For digest email, email_notification_digest must also be enabled."
        ),
    }
    reminder_map = dict(REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY)
    transactional = sorted(
        TRANSACTIONAL_NOTIFICATION_ROUTES,
        key=lambda row: row["route_key"],
    )
    tx_by_cat = build_transactional_route_keys_by_settings_category()
    return {
        "schema_version": 11,
        "reference_api_access": dict(REFERENCE_API_ACCESS),
        "settings_categories": categories,
        "transactional_routes": transactional,
        "transactional_route_keys_by_settings_category": tx_by_cat,
        "reminder_event_type_to_settings_category": reminder_map,
        "reminder_event_type_descriptions": {
            k: REMINDER_EVENT_TYPE_DESCRIPTIONS[k] for k in reminder_map
        },
        "reminder_event_type_recipient_summaries": {
            k: REMINDER_EVENT_TYPE_RECIPIENT_SUMMARIES[k] for k in reminder_map
        },
        "reminder_default_settings_category": "programs",
        "digest": {
            "settings_category": "system",
            "email_gates": ["email_system", "email_notification_digest"],
            "inapp_user_settings_field": "inapp_system",
            "typical_triggers": DIGEST_TYPICAL_TRIGGERS,
            "recipient_summary": DIGEST_RECIPIENT_SUMMARY,
        },
    }
