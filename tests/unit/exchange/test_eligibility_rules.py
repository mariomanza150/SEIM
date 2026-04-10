"""Structured eligibility rules engine."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from accounts.models import Profile, Role
from accounts.signals import create_user_profile
from documents.models import DocumentType

from exchange.eligibility_rules import evaluate_eligibility
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.mark.django_db
class TestEligibilityRulesEngine:
    def _student_with_profile(self, **profile_defaults):
        user = User.objects.create(
            username=f"stu_{Profile.objects.count()}",
            email=f"stu_{Profile.objects.count()}@test.com",
            password="x",
        )
        role, _ = Role.objects.get_or_create(name="student")
        user.roles.add(role)
        Profile.objects.update_or_create(user=user, defaults=profile_defaults)
        return user

    def test_additional_language_satisfies_required_language(self):
        user = self._student_with_profile(
            gpa=3.6,
            language="Spanish",
            language_level="B1",
            additional_languages=[{"name": "English", "level": "C1"}],
        )
        program = Program.objects.create(
            name="P1",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
            required_language="English",
            min_language_level="B2",
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is True
        ids = [r.rule_id for r in ev.rules]
        assert ids == [
            "application_window",
            "gpa",
            "required_language",
            "language_proficiency",
            "age",
        ]
        win = next(r for r in ev.rules if r.rule_id == "application_window")
        assert win.skipped is True
        lang_rule = next(r for r in ev.rules if r.rule_id == "required_language")
        assert lang_rule.passed is True
        cefr = next(r for r in ev.rules if r.rule_id == "language_proficiency")
        assert cefr.passed is True

    def test_additional_language_wrong_level_fails(self):
        user = self._student_with_profile(
            gpa=3.6,
            language="Spanish",
            language_level="C2",
            additional_languages=[{"name": "English", "level": "B1"}],
        )
        program = Program.objects.create(
            name="P2",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
            required_language="English",
            min_language_level="B2",
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert any("Language proficiency below requirement" in f for f in ev.failures)

    def test_application_window_closed_fails(self):
        user = self._student_with_profile(
            gpa=3.6,
            language="English",
            language_level="B2",
        )
        program = Program.objects.create(
            name="Closed",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
            application_open_date=date.today() - timedelta(days=30),
            application_deadline=date.today() - timedelta(days=1),
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert any("Applications closed on" in f for f in ev.failures)
        win = next(r for r in ev.rules if r.rule_id == "application_window")
        assert win.passed is False
        assert win.skipped is False

    def test_application_window_not_yet_open_fails(self):
        user = self._student_with_profile(
            gpa=3.6,
            language="English",
            language_level="B2",
        )
        program = Program.objects.create(
            name="Future",
            description="d",
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=180),
            application_open_date=date.today() + timedelta(days=5),
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert any("Applications open on" in f for f in ev.failures)

    def test_rules_payload_includes_skipped_flags(self):
        user = self._student_with_profile(gpa=3.5, language="English", language_level="B2")
        program = Program.objects.create(
            name="P3",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is True
        d = ev.rules_as_dicts()
        assert all("id" in x and "passed" in x and "skipped" in x for x in d)

    def test_required_documents_skipped_when_no_application_context(self):
        user = self._student_with_profile(
            gpa=3.5,
            language="English",
            language_level="B2",
        )
        dt = DocumentType.objects.create(name="Transcript", description="")
        program = Program.objects.create(
            name="DocProg",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
        )
        program.required_document_types.add(dt)
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is True
        rd = next(r for r in ev.rules if r.rule_id == "required_documents")
        assert rd.skipped is True

    def test_required_documents_fail_for_incomplete_application(self):
        user = self._student_with_profile(
            gpa=3.5,
            language="English",
            language_level="B2",
        )
        dt = DocumentType.objects.create(name="Passport", description="")
        program = Program.objects.create(
            name="DocProg2",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
        )
        program.required_document_types.add(dt)
        draft, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=user,
            program=program,
            status=draft,
        )
        ev = evaluate_eligibility(user, program, application=app)
        assert ev.eligible is False
        assert any(
            "Required documents are not all approved yet" in f for f in ev.failures
        )
        rd = next(r for r in ev.rules if r.rule_id == "required_documents")
        assert rd.passed is False
        assert rd.skipped is False

    def test_missing_profile_single_failure(self):
        post_save.disconnect(create_user_profile, sender=User)
        try:
            user = User.objects.create(username="noprof", email="nop@test.com", password="x")
        finally:
            post_save.connect(create_user_profile, sender=User)
        Profile.objects.filter(user=user).delete()
        program = Program.objects.create(
            name="P4",
            description="d",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=120),
        )
        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert ev.failures == ["Student profile is missing."]
