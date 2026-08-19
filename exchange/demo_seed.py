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
    {
        "username": "student_waitlist",
        "email": "student.waitlist@test.com",
        "password": "student123",
        "first_name": "Elena",
        "last_name": "Vargas",
        "role": "student",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "secondary_email": "elena.vargas@example.edu",
            "gpa": 3.5,
            "language": "German",
            "language_level": "B2",
        },
    },
    {
        "username": "partner",
        "email": "partner@test.com",
        "password": "partner123",
        "first_name": "Ines",
        "last_name": "Partner",
        "role": "partner",
        "is_staff": False,
        "is_superuser": False,
    },
]

# Manual-QA fixtures recreated by `seed_demo_readiness` (closed window, submit gate, resubmit, §8).
DEMO_CLOSED_WINDOW_PROGRAM = "DEMO-SEED Closed Window - University of Oslo"
DEMO_SUBMIT_GATE_PROGRAM = "DEMO-SEED Submit Gate - University of Lisbon"
DEMO_RESUBMIT_PROGRAM = "DEMO-SEED Resubmit - University of Vienna"
DEMO_LIFECYCLE_PROGRAM = "DEMO-SEED Lifecycle - University of Porto"

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
        "application_form_name": "Demo exchange application",
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
        "enrollment_capacity": 1,
        "waitlist_when_full": True,
        "workflow_slug": "demo-application-workflow",
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
        "eligibility_ruleset_name": "Demo Fulbright GPA overlay",
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
    {
        "name": DEMO_CLOSED_WINDOW_PROGRAM,
        "description": (
            "Manual QA 2.8 fixture: active-looking program whose application window "
            "is already closed. Create/submit must be blocked in the SPA."
        ),
        "min_gpa": 3.0,
        "required_language": "English",
        "min_language_level": "B2",
        "is_active": True,
        "window": "closed",
    },
    {
        "name": DEMO_SUBMIT_GATE_PROGRAM,
        "description": (
            "Manual QA 3.5 fixture: required checklist files are uploaded but not "
            "staff-approved, so student Submit stays blocked until a coordinator validates."
        ),
        "min_gpa": 3.0,
        "required_language": "English",
        "min_language_level": "B2",
        "is_active": True,
    },
    {
        "name": DEMO_RESUBMIT_PROGRAM,
        "description": (
            "Manual QA 3.4 fixture: submitted application with an open document "
            "resubmission request so the student can replace the file."
        ),
        "min_gpa": 3.0,
        "required_language": "English",
        "min_language_level": "B2",
        "is_active": True,
    },
    {
        "name": DEMO_LIFECYCLE_PROGRAM,
        "description": (
            "Reserved open program for Manual QA Section 8. Seed does not create a "
            "student application — create a new draft here for submit → approve."
        ),
        "min_gpa": 3.0,
        "required_language": "English",
        "min_language_level": "B2",
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
        "required_gpa": 3.0,
        "language_requirements": [
            {"lang": "Spanish", "level": "B1"},
            {"lang": "English", "level": "B2"},
        ],
        "custom_tags": "Habla Hispana",
        "application_limit": 25,
        "notify_on_limit_reached": True,
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
        "required_gpa": 3.2,
        "language_requirements": [{"lang": "German", "level": "B2"}],
        "custom_tags": "Foreign Language",
        "application_limit": 15,
        "notify_on_limit_reached": True,
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
        "required_gpa": 3.3,
        "language_requirements": [{"lang": "French", "level": "B2"}],
        "custom_tags": "Foreign Language",
        "application_limit": 10,
        "notify_on_limit_reached": True,
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
        "required_gpa": 3.5,
        "language_requirements": [{"lang": "English", "level": "C1"}],
        "custom_tags": "Foreign Language",
        "application_limit": 5,
        "notify_on_limit_reached": True,
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
        "required_gpa": 3.4,
        "language_requirements": [
            {"lang": "Japanese", "level": "N3"},
            {"lang": "English", "level": "B2"},
        ],
        "custom_tags": "Foreign Language",
        "application_limit": 8,
        "notify_on_limit_reached": False,
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
        "nomination_rank": None,
    },
    {
        "student_username": "student",
        "program_name": "Fulbright Program - Harvard University, USA",
        "status": "submitted",
        "submitted_days_ago": 3,
        "withdrawn": False,
        "nomination_rank": 2,
    },
    {
        "student_username": "student_review",
        "program_name": "DAAD Exchange - Technical University of Munich, Germany",
        "status": "under_review",
        "submitted_days_ago": 10,
        "withdrawn": False,
        "nomination_rank": 1,
    },
    {
        "student_username": "student_approved",
        "program_name": "Sciences Po Exchange - Paris, France",
        "status": "approved",
        "submitted_days_ago": 21,
        "withdrawn": False,
        "nomination_rank": 1,
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
    {
        "student_username": "student_waitlist",
        "program_name": "DAAD Exchange - Technical University of Munich, Germany",
        "status": "waitlist",
        "submitted_days_ago": 2,
        "withdrawn": False,
        "nomination_rank": 4,
    },
    {
        "student_username": "student",
        "program_name": "Movilidad Internacional Habla Inglesa",
        "status": "draft",
        "submitted_days_ago": None,
        "withdrawn": False,
    },
    {
        "student_username": "student",
        "program_name": DEMO_SUBMIT_GATE_PROGRAM,
        "status": "draft",
        "submitted_days_ago": None,
        "withdrawn": False,
        "seed_required_docs_unapproved": True,
    },
    {
        "student_username": "student",
        "program_name": DEMO_RESUBMIT_PROGRAM,
        "status": "submitted",
        "submitted_days_ago": 4,
        "withdrawn": False,
        "open_resubmission": True,
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
    return sorted(
        {spec["username"] for spec in DEMO_USER_SPECS} | set(LEGACY_DEMO_USERS)
    )


def demo_emails():
    return sorted({spec["email"] for spec in DEMO_USER_SPECS} | {"test@example.com"})


def demo_program_names():
    return sorted(
        {spec["name"] for spec in DEMO_PROGRAM_SPECS} | set(LEGACY_DEMO_PROGRAM_NAMES)
    )


DEMO_ALLOWED_EMAIL_DOMAINS = (
    ("test.com", "test"),
    ("example.edu", "example_edu"),
    ("university.edu", "university"),
    ("seim.edu", "seim"),
    ("uadec.edu.mx", "uadec"),
)

DEMO_FORM_NAME = "Demo exchange application"
DEMO_FORM_STEP_TEMPLATE_SLUG = "demo-motivation"
DEMO_WORKFLOW_SLUG = "demo-application-workflow"
DEMO_WORKFLOW_NAME = "Demo application workflow"
DEMO_ELIGIBILITY_RULESET_NAME = "Demo Fulbright GPA overlay"
DEMO_PARTNER_AGREEMENT_REF = "DEMO-SEED-AGR-001"

DEMO_BPMN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  id="Definitions_demo"
  targetNamespace="http://seim.local/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start" />
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="UserTask_1" />
    <bpmn:userTask id="UserTask_1" name="submitted" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="180" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="UserTask_1_di" bpmnElement="UserTask_1">
        <dc:Bounds x="260" y="78" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <dc:Bounds x="0" y="0" width="0" height="0" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""

DEMO_HOST_SPECS = {
    "Erasmus+ Exchange - University of Barcelona, Spain": {
        "country": "Spain",
        "institution": "Universitat de Barcelona",
        "school": "Faculty of Economics",
        "academic": "International Business",
        "academic_code": "IB",
        "subjects": (
            {"code": "IB201", "name": "Mediterranean Markets", "credits": "6.00"},
            {"code": "IB210", "name": "Spanish for Exchange", "credits": "4.00"},
        ),
    },
    "DAAD Exchange - Technical University of Munich, Germany": {
        "country": "Germany",
        "institution": "Technical University of Munich",
        "school": "Department of Informatics",
        "academic": "Computer Science",
        "academic_code": "CS",
        "subjects": (
            {"code": "IN0001", "name": "Algorithms", "credits": "6.00"},
            {"code": "IN0008", "name": "Software Engineering", "credits": "5.00"},
        ),
    },
    "Fulbright Program - Harvard University, USA": {
        "country": "USA",
        "institution": "Harvard University",
        "school": "Faculty of Arts and Sciences",
        "academic": "Government",
        "academic_code": "GOV",
        "subjects": (
            {"code": "GOV100", "name": "Comparative Politics", "credits": "4.00"},
        ),
    },
    "Exchange Program - University of Tokyo, Japan": {
        "country": "Japan",
        "institution": "University of Tokyo",
        "school": "Graduate School of Engineering",
        "academic": "Information Science",
        "academic_code": "IS",
        "subjects": ({"code": "IS301", "name": "Machine Learning", "credits": "2.00"},),
    },
    "Sorbonne Exchange - Paris, France": {
        "country": "France",
        "institution": "Sorbonne University",
        "school": "Faculty of Letters",
        "academic": "History",
        "academic_code": "HIS",
        "subjects": (
            {"code": "HIS210", "name": "European History", "credits": "6.00"},
        ),
    },
    "Sciences Po Exchange - Paris, France": {
        "country": "France",
        "institution": "Sciences Po",
        "school": "School of Public Affairs",
        "academic": "International Relations",
        "academic_code": "IR",
        "subjects": ({"code": "IR101", "name": "European Policy", "credits": "6.00"},),
    },
    "Movilidad Internacional Habla Hispana": {
        "country": "España",
        "institution": "Universidad de León",
        "school": "Facultad / Escuela general",
        "academic": "Programa académico general",
        "academic_code": "GEN",
        "subjects": (
            {"code": "GEN101", "name": "Asignatura general de movilidad", "credits": "6.00"},
        ),
    },
    "Movilidad Internacional Habla Inglesa": {
        "country": "Italia",
        "institution": "Università degli Studi di Firenze",
        "school": "Facultad / Escuela general",
        "academic": "Programa académico general",
        "academic_code": "GEN",
        "subjects": (
            {"code": "GEN101", "name": "Asignatura general de movilidad", "credits": "6.00"},
        ),
    },
    "Movilidad Internacional": {
        "country": "Italia",
        "institution": "Università degli Studi di Firenze",
        "school": "Facultad / Escuela general",
        "academic": "Programa académico general",
        "academic_code": "GEN",
        "subjects": (
            {"code": "GEN101", "name": "Asignatura general de movilidad", "credits": "6.00"},
        ),
    },
    DEMO_CLOSED_WINDOW_PROGRAM: {
        "country": "Norway",
        "institution": "University of Oslo",
        "school": "Faculty of Mathematics and Natural Sciences",
        "academic": "Informatics",
        "academic_code": "INF",
        "subjects": (
            {"code": "INF100", "name": "Introduction to Programming", "credits": "10.00"},
        ),
    },
    DEMO_SUBMIT_GATE_PROGRAM: {
        "country": "Portugal",
        "institution": "University of Lisbon",
        "school": "Instituto Superior Técnico",
        "academic": "Information Systems",
        "academic_code": "IS",
        "subjects": ({"code": "IS201", "name": "Databases", "credits": "6.00"},),
    },
    DEMO_RESUBMIT_PROGRAM: {
        "country": "Austria",
        "institution": "University of Vienna",
        "school": "Faculty of Computer Science",
        "academic": "Software Engineering",
        "academic_code": "SE",
        "subjects": (
            {"code": "SE110", "name": "Requirements Engineering", "credits": "6.00"},
        ),
    },
    DEMO_LIFECYCLE_PROGRAM: {
        "country": "Portugal",
        "institution": "University of Porto",
        "school": "Faculty of Engineering",
        "academic": "Informatics Engineering",
        "academic_code": "EIC",
        "subjects": (
            {"code": "EIC001", "name": "Programming Fundamentals", "credits": "6.00"},
        ),
    },
}
