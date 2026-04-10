"""Unit tests for exchange.scholarship_scoring."""

from datetime import timedelta

import pytest
from django.utils import timezone

from exchange.scholarship_scoring import (
    RULESET_ID,
    build_scholarship_scores_csv,
    compute_scholarship_allocation_score,
    rank_applications_for_scholarship,
    render_scholarship_scores_xlsx,
    scholarship_scores_export_response,
)
from tests.utils import TestUtils


@pytest.mark.django_db
class TestScholarshipScoringCompute:
    def test_ruleset_and_factors_present(self):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        app = TestUtils.create_test_application(
            student=student, program=program, status_name="submitted"
        )
        out = compute_scholarship_allocation_score(app)
        assert out["ruleset_id"] == RULESET_ID
        assert len(out["factors"]) == 5
        ids = {f["id"] for f in out["factors"]}
        assert ids == {
            "academic",
            "language",
            "program_fit",
            "application_quality",
            "timeliness",
        }
        assert 0 <= out["total_points"] <= out["max_points"]

    def test_no_gpa_zero_academic(self):
        student = TestUtils.create_test_user(role="student")
        student.profile.gpa = None
        student.profile.save(update_fields=["gpa"])
        program = TestUtils.create_test_program()
        app = TestUtils.create_test_application(
            student=student, program=program, status_name="submitted"
        )
        out = compute_scholarship_allocation_score(app)
        ac = next(f for f in out["factors"] if f["id"] == "academic")
        assert ac["points"] == 0.0

    def test_language_meets_program_minimum(self):
        student = TestUtils.create_test_user(role="student")
        student.profile.language_level = "B2"
        student.profile.save(update_fields=["language_level"])
        program = TestUtils.create_test_program()
        program.min_language_level = "B1"
        program.save(update_fields=["min_language_level"])
        app = TestUtils.create_test_application(
            student=student, program=program, status_name="submitted"
        )
        out = compute_scholarship_allocation_score(app)
        lang = next(f for f in out["factors"] if f["id"] == "language")
        assert lang["points"] >= 18.0

    def test_timeliness_early_window(self):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        today = timezone.localdate()
        program.application_open_date = today - timedelta(days=30)
        program.application_deadline = today + timedelta(days=30)
        program.save(update_fields=["application_open_date", "application_deadline"])
        app = TestUtils.create_test_application(
            student=student, program=program, status_name="submitted"
        )
        app.submitted_at = timezone.now() - timedelta(days=25)
        app.save(update_fields=["submitted_at"])
        out = compute_scholarship_allocation_score(app)
        tim = next(f for f in out["factors"] if f["id"] == "timeliness")
        assert tim["points"] == 15.0


@pytest.mark.django_db
class TestScholarshipScoringCohort:
    def test_rank_orders_by_total_desc(self):
        program = TestUtils.create_test_program()
        s_low = TestUtils.create_test_user(role="student", username="s_low")
        s_low.profile.gpa = 3.0
        s_low.profile.save(update_fields=["gpa"])
        s_high = TestUtils.create_test_user(role="student", username="s_high")
        s_high.profile.gpa = 3.9
        s_high.profile.save(update_fields=["gpa"])
        a1 = TestUtils.create_test_application(
            student=s_low, program=program, status_name="submitted"
        )
        a2 = TestUtils.create_test_application(
            student=s_high, program=program, status_name="submitted"
        )
        ranked = rank_applications_for_scholarship([a1, a2])
        assert ranked[0].rank == 1
        assert ranked[1].rank == 2
        assert ranked[0].score["total_points"] >= ranked[1].score["total_points"]

    def test_csv_contains_headers_and_rank(self):
        program = TestUtils.create_test_program()
        student = TestUtils.create_test_user(role="student")
        TestUtils.create_test_application(student=student, program=program, status_name="submitted")
        qs = program.application_set.all()
        csv_text = build_scholarship_scores_csv(qs)
        lines = csv_text.strip().splitlines()
        assert "rank" in lines[0]
        assert "ruleset_id" in lines[0]
        assert len(lines) >= 2
        assert RULESET_ID in lines[1]

    def test_xlsx_starts_with_zip_signature(self):
        program = TestUtils.create_test_program()
        student = TestUtils.create_test_user(role="student")
        TestUtils.create_test_application(student=student, program=program, status_name="submitted")
        raw = render_scholarship_scores_xlsx(program.application_set.all())
        assert raw[:2] == b"PK"

    def test_export_response_rejects_bad_format(self):
        program = TestUtils.create_test_program()
        with pytest.raises(ValueError):
            scholarship_scores_export_response(
                program.id, program.application_set.all(), export_format="rtf"
            )
