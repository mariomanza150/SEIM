"""Demo accounts that testers may switch into (seeded by seed_test_accounts)."""

from django.contrib.auth import get_user_model

from exchange.demo_seed import DEMO_USER_SPECS

# Extra accounts beyond the canonical demo dataset.
EXTRA_DEMO_SPECS = [
    {
        "username": "student.new",
        "email": "student.new@test.com",
        "first_name": "Nora",
        "last_name": "Newcomer",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "description": "Fresh student with no applications (onboarding flows).",
    },
]

# Legacy demo accounts created by older seed commands; rotated + flagged if present.
LEGACY_DEMO_EMAILS = [
    "test@example.com",
    "admin@seim.local",
    "coordinator@seim.local",
    "student@university.edu",
]

DESCRIPTIONS = {
    "admin@test.com": "SEIM admin console (programs, users, workflows). Not a superuser.",
    "coordinator@test.com": "Coordinator: review queue, documents, nominations.",
    "student@test.com": "Student with applications in progress.",
    "student.review@test.com": "Student with an application under review.",
    "student.approved@test.com": "Student with an approved application.",
    "student.rejected@test.com": "Student with a rejected application.",
    "student.completed@test.com": "Student with a completed exchange.",
    "student.cancelled@test.com": "Student with a cancelled application.",
    "student.waitlist@test.com": "Student on a waitlist.",
    "student.nominated@test.com": "Nominated student (partner acknowledgement flow).",
    "partner@test.com": "Partner institution portal.",
    "student.new@test.com": "Fresh student with no applications (onboarding flows).",
}


def all_demo_specs():
    return list(DEMO_USER_SPECS) + list(EXTRA_DEMO_SPECS)


def demo_queryset():
    return (
        get_user_model()
        .objects.filter(is_demo_account=True, is_active=True, is_superuser=False)
        .prefetch_related("roles")
        .order_by("email")
    )
