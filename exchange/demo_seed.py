"""Shared constants for the canonical SEIM demo dataset."""

DEMO_USER_SPECS = [
    {
        "username": "admin",
        "email": "admin@test.com",
        "password": "admin123",
        "first_name": "Alex",
        "last_name": "Administrator",
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "coordinator",
        "email": "coordinator@test.com",
        "password": "coordinator123",
        "first_name": "Camila",
        "last_name": "Coordinator",
        "role": "coordinator",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "username": "student",
        "email": "student@test.com",
        "password": "student123",
        "first_name": "Sofia",
        "last_name": "Martinez",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "sofia.martinez@example.edu",
            "gpa": 3.7,
            "language": "English",
            "language_level": "C1",
        },
    },
    {
        "username": "student_review",
        "email": "student.review@test.com",
        "password": "student123",
        "first_name": "Diego",
        "last_name": "Lopez",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "diego.lopez@example.edu",
            "gpa": 3.4,
            "language": "German",
            "language_level": "B2",
        },
    },
    {
        "username": "student_approved",
        "email": "student.approved@test.com",
        "password": "student123",
        "first_name": "Lucia",
        "last_name": "Fernandez",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "lucia.fernandez@example.edu",
            "gpa": 3.8,
            "language": "English",
            "language_level": "C1",
        },
    },
    {
        "username": "student_rejected",
        "email": "student.rejected@test.com",
        "password": "student123",
        "first_name": "Mateo",
        "last_name": "Rojas",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "mateo.rojas@example.edu",
            "gpa": 2.6,
            "language": "French",
            "language_level": "A2",
        },
    },
    {
        "username": "student_completed",
        "email": "student.completed@test.com",
        "password": "student123",
        "first_name": "Valentina",
        "last_name": "Silva",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "valentina.silva@example.edu",
            "gpa": 3.9,
            "language": "Spanish",
            "language_level": "C2",
        },
    },
    {
        "username": "student_cancelled",
        "email": "student.cancelled@test.com",
        "password": "student123",
        "first_name": "Andres",
        "last_name": "Gomez",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "andres.gomez@example.edu",
            "gpa": 3.1,
            "language": "Japanese",
            "language_level": "B1",
        },
    },
]

DEMO_PROGRAM_SPECS = [
    {
        "name": "Erasmus+ Exchange - University of Barcelona, Spain",
        "description": (
            "Semester exchange focused on business, communication, and Mediterranean "
            "culture with courses offered in English and Spanish."
        ),
        "min_gpa": 3.0,
        "required_language": "Spanish",
        "min_language_level": "B1",
        "is_active": True,
    },
    {
        "name": "DAAD Exchange - Technical University of Munich, Germany",
        "description": (
            "Engineering and computer science exchange with strong research labs "
            "and industry collaboration in Munich."
        ),
        "min_gpa": 3.3,
        "required_language": "German",
        "min_language_level": "B2",
        "is_active": True,
    },
    {
        "name": "Fulbright Program - Harvard University, USA",
        "description": (
            "Highly selective academic exchange for high-performing students across "
            "multiple disciplines with scholarship support."
        ),
        "min_gpa": 3.7,
        "required_language": "English",
        "min_language_level": "C1",
        "is_active": True,
    },
    {
        "name": "Exchange Program - University of Tokyo, Japan",
        "description": (
            "Academic and cultural immersion program with optional Japanese language "
            "support in Tokyo."
        ),
        "min_gpa": 3.2,
        "required_language": "Japanese",
        "min_language_level": "B1",
        "is_active": True,
    },
    {
        "name": "Sorbonne Exchange - Paris, France",
        "description": (
            "Humanities and social sciences semester abroad with strong French "
            "language immersion."
        ),
        "min_gpa": 2.8,
        "required_language": "French",
        "min_language_level": "B2",
        "is_active": True,
    },
    {
        "name": "Sciences Po Exchange - Paris, France",
        "description": (
            "Political science and international relations exchange taught primarily "
            "in English with a European policy focus."
        ),
        "min_gpa": 3.4,
        "required_language": "English",
        "min_language_level": "C1",
        "is_active": True,
    },
]

# Staff exchange-agreement registry (`/seim/exchange-agreements`). Seeded by `seed_demo_readiness`.
# Offsets are days relative to the seed run date (`base_date` in the command).
DEMO_AGREEMENT_SPECS = [
    {
        "internal_reference": "DEMO-SEED-AGR-001",
        "title": "Erasmus+ framework — Catalonia cluster",
        "partner_institution_name": "Universitat de Barcelona",
        "partner_country": "Spain",
        "partner_reference_id": "UB-ERASMUS-2019",
        "agreement_type": "erasmus",
        "status": "active",
        "notes": "Demo active agreement linked to the Barcelona program.",
        "program_names": ["Erasmus+ Exchange - University of Barcelona, Spain"],
        "start_offset_days": -400,
        "end_offset_days": 500,
    },
    {
        "internal_reference": "DEMO-SEED-AGR-002",
        "title": "DAAD bilateral cooperation",
        "partner_institution_name": "Technical University of Munich",
        "partner_country": "Germany",
        "agreement_type": "bilateral",
        "status": "active",
        "program_names": ["DAAD Exchange - Technical University of Munich, Germany"],
        "start_offset_days": -200,
        "end_offset_days": 300,
    },
    {
        "internal_reference": "DEMO-SEED-AGR-003",
        "title": "Sorbonne mobility (draft renewal package)",
        "partner_institution_name": "Sorbonne University",
        "partner_country": "France",
        "agreement_type": "bilateral",
        "status": "draft",
        "program_names": ["Sorbonne Exchange - Paris, France"],
        "start_offset_days": -30,
        "end_offset_days": 120,
    },
    {
        "internal_reference": "DEMO-SEED-AGR-004",
        "title": "Fulbright institutional agreement",
        "partner_institution_name": "Harvard University",
        "partner_country": "USA",
        "agreement_type": "specific",
        "status": "renewal_pending",
        "notes": "Demo row for renewal follow-up filters.",
        "program_names": ["Fulbright Program - Harvard University, USA"],
        "start_offset_days": -800,
        "end_offset_days": 60,
        "renewal_follow_up_due_offset_days": 45,
    },
    {
        "internal_reference": "DEMO-SEED-AGR-005",
        "title": "Tokyo exchange (superseded)",
        "partner_institution_name": "University of Tokyo",
        "partner_country": "Japan",
        "agreement_type": "bilateral",
        "status": "expired",
        "program_names": ["Exchange Program - University of Tokyo, Japan"],
        "start_offset_days": -900,
        "end_offset_days": -45,
    },
]

DEMO_APPLICATION_SPECS = [
    {
        "student_username": "student",
        "program_name": "Erasmus+ Exchange - University of Barcelona, Spain",
        "status": "draft",
        "submitted_days_ago": None,
        "withdrawn": False,
    },
    {
        "student_username": "student",
        "program_name": "Fulbright Program - Harvard University, USA",
        "status": "submitted",
        "submitted_days_ago": 3,
        "withdrawn": False,
    },
    {
        "student_username": "student_review",
        "program_name": "DAAD Exchange - Technical University of Munich, Germany",
        "status": "under_review",
        "submitted_days_ago": 10,
        "withdrawn": False,
    },
    {
        "student_username": "student_approved",
        "program_name": "Sciences Po Exchange - Paris, France",
        "status": "approved",
        "submitted_days_ago": 21,
        "withdrawn": False,
    },
    {
        "student_username": "student_rejected",
        "program_name": "Sorbonne Exchange - Paris, France",
        "status": "rejected",
        "submitted_days_ago": 18,
        "withdrawn": False,
    },
    {
        "student_username": "student_completed",
        "program_name": "Exchange Program - University of Tokyo, Japan",
        "status": "completed",
        "submitted_days_ago": 45,
        "withdrawn": False,
    },
    {
        "student_username": "student_cancelled",
        "program_name": "Erasmus+ Exchange - University of Barcelona, Spain",
        "status": "cancelled",
        "submitted_days_ago": 7,
        "withdrawn": True,
    },
]

LEGACY_DEMO_PROGRAM_NAMES = [
    "Erasmus+ Computer Science Exchange",
    "Business Administration in Spain",
    "Engineering Exchange in Germany",
    "Arts and Culture in France",
    "Environmental Science in Scandinavia",
    "Medical Research Exchange",
    "Language Immersion in Italy",
    "Summer Research Program",
    "Vue E2E Test Program",
]

LEGACY_DEMO_USERS = [
    "testuser",
]


def demo_usernames():
    return sorted({spec["username"] for spec in DEMO_USER_SPECS} | set(LEGACY_DEMO_USERS))


def demo_emails():
    return sorted({spec["email"] for spec in DEMO_USER_SPECS} | {"test@example.com"})


def demo_program_names():
    return sorted(
        {spec["name"] for spec in DEMO_PROGRAM_SPECS} | set(LEGACY_DEMO_PROGRAM_NAMES)
    )
