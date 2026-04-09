from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role, User
from application_forms.models import FormSubmission, FormType
from documents.models import Document, DocumentType
from exchange.models import ApplicationStatus, Program


class TestApplicationDynamicFormAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.student = User.objects.create_user(
            username="dynamic-form-student",
            email="dynamic-form-student@example.com",
            password="testpass123",
        )
        self.student.roles.add(self.student_role)
        self.coordinator = User.objects.create_user(
            username="dynamic-form-coordinator",
            email="dynamic-form-coordinator@example.com",
            password="testpass123",
        )
        self.coordinator.roles.add(self.coordinator_role)
        self.client.force_authenticate(user=self.student)

        self.form_type = FormType.objects.create(
            name="Exchange Questions",
            form_type="application",
            schema={
                "properties": {
                    "motivation": {"type": "string", "title": "Motivation"},
                    "academic_goals": {"type": "string", "title": "Academic Goals"},
                },
                "required": ["motivation", "academic_goals"],
            },
            created_by=self.student,
        )
        self.program = Program.objects.create(
            name="Dynamic Program",
            description="Program with schema-driven questions",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=120),
            is_active=True,
            application_form=self.form_type,
        )
        self.program.coordinators.add(self.coordinator)
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1},
        )
        ApplicationStatus.objects.get_or_create(
            name="submitted",
            defaults={"order": 2},
        )

    def test_create_application_with_dynamic_form_submission(self):
        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "I want to broaden my academic perspective.",
                "df_academic_goals": "Study international policy.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission = FormSubmission.objects.get(application_id=response.data["id"])
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(
            submission.responses["motivation"],
            "I want to broaden my academic perspective.",
        )
        application = self.program.application_set.get(id=response.data["id"])
        self.assertEqual(application.assigned_coordinator, self.coordinator)

        detail_response = self.client.get(
            reverse("api:application-detail", args=[response.data["id"]])
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            detail_response.data["dynamic_form_submission"]["responses"]["academic_goals"],
            "Study international policy.",
        )
        self.assertEqual(
            str(detail_response.data["assigned_coordinator"]),
            str(self.coordinator.id),
        )
        self.assertEqual(
            str(detail_response.data["effective_coordinator"]["id"]),
            str(self.coordinator.id),
        )

    def test_create_application_with_missing_required_dynamic_field_fails(self):
        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "I want to broaden my academic perspective.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("dynamic_form", response.data)
        self.assertEqual(FormSubmission.objects.count(), 0)

    def test_create_application_after_deadline_fails(self):
        self.program.application_open_date = timezone.localdate() - timedelta(days=30)
        self.program.application_deadline = timezone.localdate() - timedelta(days=1)
        self.program.save(update_fields=["application_open_date", "application_deadline"])

        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "I want to broaden my academic perspective.",
                "df_academic_goals": "Study international policy.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("program", response.data)
        self.assertIn("Applications closed on", response.data["program"][0])

    def test_student_cannot_set_assigned_coordinator_directly(self):
        other_coordinator = User.objects.create_user(
            username="other-coordinator",
            email="other-coordinator@example.com",
            password="testpass123",
        )
        other_coordinator.roles.add(self.coordinator_role)

        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "assigned_coordinator": str(other_coordinator.id),
                "df_motivation": "I want to broaden my academic perspective.",
                "df_academic_goals": "Study international policy.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        application = self.program.application_set.get(id=response.data["id"])
        self.assertEqual(application.assigned_coordinator, self.coordinator)

    def test_multistep_partial_create_succeeds(self):
        self.form_type.step_definitions = [
            {"key": "s1", "title": "Step 1", "field_names": ["motivation"]},
            {"key": "s2", "title": "Step 2", "field_names": ["academic_goals"]},
        ]
        self.form_type.save()

        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "Step one answer.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission = FormSubmission.objects.get(application_id=response.data["id"])
        self.assertEqual(submission.responses.get("motivation"), "Step one answer.")
        self.assertNotIn("academic_goals", submission.responses)
        application = self.program.application_set.get(id=response.data["id"])
        self.assertEqual(application.dynamic_form_current_step, "s1")

    def test_multistep_requires_current_step_key(self):
        self.form_type.step_definitions = [
            {"key": "s1", "title": "Step 1", "field_names": ["motivation"]},
            {"key": "s2", "title": "Step 2", "field_names": ["academic_goals"]},
        ]
        self.form_type.save()

        response = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "Step one answer.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("dynamic_form", response.data)

    def test_submit_fails_until_multistep_form_complete(self):
        self.form_type.step_definitions = [
            {"key": "s1", "title": "Step 1", "field_names": ["motivation"]},
            {"key": "s2", "title": "Step 2", "field_names": ["academic_goals"]},
        ]
        self.form_type.save()

        create_resp = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "Done step 1.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        app_id = create_resp.data["id"]
        self.assertEqual(create_resp.data["dynamic_form_layout"]["current_step"], "s1")

        submit_resp = self.client.post(
            reverse("api:application-submit", args=[app_id]),
            {},
            format="json",
        )
        self.assertEqual(submit_resp.status_code, status.HTTP_400_BAD_REQUEST)

        advance1 = self.client.patch(
            reverse("api:application-detail", args=[app_id]),
            {
                "df_motivation": "Done step 1.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(advance1.status_code, status.HTTP_200_OK)
        self.assertEqual(advance1.data["dynamic_form_layout"]["current_step"], "s2")

        patch_resp = self.client.patch(
            reverse("api:application-detail", args=[app_id]),
            {
                "df_academic_goals": "Done step 2.",
                "dynamic_form_current_step": "s2",
            },
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)

        submit_ok = self.client.post(
            reverse("api:application-submit", args=[app_id]),
            {},
            format="json",
        )
        self.assertEqual(submit_ok.status_code, status.HTTP_200_OK)

    def test_multistep_advancing_blocked_until_step_documents_approved(self):
        dt = DocumentType.objects.create(name="Step1 Doc", description="needed for step 1")
        self.program.required_document_types.add(dt)
        self.form_type.step_definitions = [
            {
                "key": "s1",
                "title": "Step 1",
                "field_names": ["motivation"],
                "required_document_type_ids": [dt.id],
            },
            {"key": "s2", "title": "Step 2", "field_names": ["academic_goals"]},
        ]
        self.form_type.save()

        create_resp = self.client.post(
            reverse("api:application-list"),
            {
                "program": str(self.program.id),
                "df_motivation": "Done step 1.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        app_id = create_resp.data["id"]

        blocked = self.client.patch(
            reverse("api:application-detail", args=[app_id]),
            {
                "df_motivation": "Still step 1.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(blocked.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("dynamic_form", blocked.data)

        pdf = SimpleUploadedFile("stub.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        app = self.program.application_set.get(id=app_id)
        Document.objects.create(
            application=app,
            type=dt,
            file=pdf,
            uploaded_by=self.student,
            is_valid=True,
        )

        advance = self.client.patch(
            reverse("api:application-detail", args=[app_id]),
            {
                "df_motivation": "Ready.",
                "dynamic_form_current_step": "s1",
            },
            format="json",
        )
        self.assertEqual(advance.status_code, status.HTTP_200_OK)
        self.assertEqual(advance.data["dynamic_form_layout"]["current_step"], "s2")
