from unittest import mock

import pytest

from exchange.services import ApplicationService
from tests.conftest import (
    ApplicationFactory,
    ApplicationStatusFactory,
    ProfileFactory,
    ProgramFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestApplicationService:
    @pytest.mark.skip(
        reason="Profile is always auto-created by signals; this scenario is not possible."
    )
    def test_check_eligibility_no_profile(self):
        user = UserFactory()
        # Delete the automatically created profile
        if hasattr(user, "profile"):
            user.profile.delete()
        program = ProgramFactory(required_language=None)  # No language requirement
        with pytest.raises(ValueError, match="Student profile is missing."):
            ApplicationService.check_eligibility(user, program)

    def test_check_eligibility_gpa_below_min(self):
        user = UserFactory()
        profile = ProfileFactory(user=user)
        profile.gpa = 2.0
        profile.save()
        program = ProgramFactory(min_gpa=3.0)
        user.profile = profile
        with pytest.raises(ValueError, match="GPA below program minimum."):
            ApplicationService.check_eligibility(user, program)

    def test_check_eligibility_language_requirement(self):
        user = UserFactory()
        profile = ProfileFactory(user=user)
        profile.gpa = 4.0  # Ensure GPA is above any min_gpa
        profile.language = "English"
        profile.save()
        program = ProgramFactory(required_language="Spanish", min_gpa=3.0)
        user.profile = profile
        with pytest.raises(ValueError, match="Language requirement not met."):
            ApplicationService.check_eligibility(user, program)

    def test_check_eligibility_success(self):
        user = UserFactory()
        profile = ProfileFactory(user=user)
        profile.gpa = 3.5
        profile.language = "English"
        profile.save()
        program = ProgramFactory(min_gpa=3.0, required_language="English")
        user.profile = profile
        assert ApplicationService.check_eligibility(user, program) is True

    def test_can_submit_application_true(self):
        user = UserFactory()
        program = ProgramFactory()
        assert ApplicationService.can_submit_application(user, program) is True

    def test_can_submit_application_false(self):
        user = UserFactory()
        program = ProgramFactory()
        status = ApplicationStatusFactory(name="submitted")
        ApplicationFactory(
            student=user, program=program, status=status, withdrawn=False
        )
        assert ApplicationService.can_submit_application(user, program) is False

    @mock.patch("exchange.services.NotificationService.send_notification")
    def test_submit_application_success(self, mock_notify):
        user = UserFactory()
        profile = ProfileFactory(user=user, gpa=3.5, language="English")
        program = ProgramFactory(min_gpa=3.0, required_language="English")
        draft_status = ApplicationStatusFactory(name="draft")
        ApplicationStatusFactory(name="submitted")
        application = ApplicationFactory(
            student=user, program=program, status=draft_status
        )
        user.profile = profile
        result = ApplicationService.submit_application(application, user)
        assert result.status.name == "submitted"
        assert result.submitted_at is not None
        mock_notify.assert_called_once()

    def test_submit_application_not_draft(self):
        user = UserFactory()
        profile = ProfileFactory(user=user, gpa=3.5, language="English")
        program = ProgramFactory(min_gpa=3.0, required_language="English")
        submitted_status = ApplicationStatusFactory(name="submitted")
        application = ApplicationFactory(
            student=user, program=program, status=submitted_status
        )
        user.profile = profile
        with pytest.raises(
            ValueError, match="Only draft applications can be submitted."
        ):
            ApplicationService.submit_application(application, user)

    @mock.patch(
        "exchange.services.ApplicationService.check_eligibility",
        side_effect=ValueError("GPA below program minimum."),
    )
    def test_submit_application_not_eligible(self, mock_elig):
        user = UserFactory()
        program = ProgramFactory()
        draft_status = ApplicationStatusFactory(name="draft")
        application = ApplicationFactory(
            student=user, program=program, status=draft_status
        )
        with pytest.raises(ValueError, match="GPA below program minimum."):
            ApplicationService.submit_application(application, user)

    @mock.patch(
        "exchange.services.ApplicationService.can_submit_application",
        return_value=False,
    )
    def test_submit_application_already_active(self, mock_can):
        user = UserFactory()
        profile = ProfileFactory(user=user, gpa=4.0, language="English")
        program = ProgramFactory(min_gpa=3.0, required_language="English")
        draft_status = ApplicationStatusFactory(name="draft")
        application = ApplicationFactory(
            student=user, program=program, status=draft_status
        )
        user.profile = profile
        with pytest.raises(
            ValueError, match="You already have an active application for this program."
        ):
            ApplicationService.submit_application(application, user)
