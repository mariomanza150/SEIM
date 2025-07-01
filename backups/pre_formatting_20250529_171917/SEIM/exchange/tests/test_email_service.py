"""
Tests for Email Service.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from django.utils import timezone

from ..models import Exchange
from ..services.email_notifications import ExchangeEmailNotificationService
from ..services.email_service import EmailService


@pytest.mark.django_db
class TestEmailService:
    """Test suite for EmailService."""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance."""
        return EmailService()

    def test_init_with_aws_ses(self):
        """Test initialization with AWS SES enabled."""
        with override_settings(
            USE_AWS_SES=True,
            AWS_SES_REGION="us-east-1",
            AWS_ACCESS_KEY_ID="test_key",
            AWS_SECRET_ACCESS_KEY="test_secret",
        ):
            with patch("boto3.client") as mock_boto_client:
                service = EmailService()
                assert service.use_aws_ses is True
                mock_boto_client.assert_called_once_with(
                    "ses",
                    region_name="us-east-1",
                    aws_access_key_id="test_key",
                    aws_secret_access_key="test_secret",
                )

    def test_init_with_smtp(self):
        """Test initialization with SMTP (AWS SES disabled)."""
        with override_settings(USE_AWS_SES=False):
            service = EmailService()
            assert service.use_aws_ses is False
            assert not hasattr(service, "ses_client")

    @patch("exchange.services.email_service.render_to_string")
    @patch("exchange.services.email_service.strip_tags")
    def test_send_email_via_smtp(self, mock_strip_tags, mock_render_to_string):
        """Test sending email via SMTP."""
        mock_render_to_string.return_value = "<html>Test HTML</html>"
        mock_strip_tags.return_value = "Test Text"

        with override_settings(
            USE_AWS_SES=False, DEFAULT_FROM_EMAIL="noreply@test.com"
        ):
            with patch(
                "exchange.services.email_service.EmailMultiAlternatives"
            ) as mock_email:
                mock_email_instance = MagicMock()
                mock_email.return_value = mock_email_instance

                service = EmailService()
                result = service.send_email(
                    to_emails=["test@example.com"],
                    subject="Test Subject",
                    template_name="test_template",
                    context={"key": "value"},
                )

                assert result is True
                mock_render_to_string.assert_called_once_with(
                    "email/test_template.html", {"key": "value"}
                )
                mock_email.assert_called_once_with(
                    subject="Test Subject",
                    body="Test Text",
                    from_email="noreply@test.com",
                    to=["test@example.com"],
                    cc=[],
                    bcc=[],
                )
                mock_email_instance.attach_alternative.assert_called_once_with(
                    "<html>Test HTML</html>", "text/html"
                )
                mock_email_instance.send.assert_called_once()

    @patch("exchange.services.email_service.render_to_string")
    @patch("exchange.services.email_service.strip_tags")
    def test_send_email_via_ses(self, mock_strip_tags, mock_render_to_string):
        """Test sending email via AWS SES."""
        mock_render_to_string.return_value = "<html>Test HTML</html>"
        mock_strip_tags.return_value = "Test Text"

        with override_settings(
            USE_AWS_SES=True,
            DEFAULT_FROM_EMAIL="noreply@test.com",
            AWS_ACCESS_KEY_ID="test_key",
            AWS_SECRET_ACCESS_KEY="test_secret",
        ):
            with patch("boto3.client") as mock_boto_client:
                mock_ses = MagicMock()
                mock_boto_client.return_value = mock_ses
                mock_ses.send_email.return_value = {"MessageId": "123456"}

                service = EmailService()
                result = service.send_email(
                    to_emails=["test@example.com"],
                    subject="Test Subject",
                    template_name="test_template",
                    context={"key": "value"},
                )

                assert result is True
                mock_ses.send_email.assert_called_once()
                call_args = mock_ses.send_email.call_args[1]
                assert call_args["Source"] == "noreply@test.com"
                assert call_args["Destination"]["ToAddresses"] == ["test@example.com"]
                assert call_args["Message"]["Subject"]["Data"] == "Test Subject"

    def test_send_email_error_handling(self):
        """Test error handling in send_email."""
        with override_settings(USE_AWS_SES=False):
            with patch(
                "exchange.services.email_service.render_to_string"
            ) as mock_render:
                mock_render.side_effect = Exception("Template error")

                service = EmailService()
                result = service.send_email(
                    to_emails=["test@example.com"],
                    subject="Test Subject",
                    template_name="test_template",
                    context={},
                )

                assert result is False


@pytest.mark.django_db
class TestExchangeEmailNotificationService:
    """Test suite for ExchangeEmailNotificationService."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @pytest.fixture
    def exchange(self, user):
        """Create a test exchange."""
        return Exchange.objects.create(
            student=user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            student_id="STU001",
            current_university="Test University",
            current_program="Computer Science",
            current_year=3,
            gpa=Decimal("3.5"),
            destination_university="MIT",
            destination_country="USA",
            exchange_program="Exchange Program A",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            status="DRAFT",
        )

    @pytest.fixture
    def notification_service(self):
        """Create notification service instance."""
        return ExchangeEmailNotificationService()

    def test_admin_emails_from_settings(self):
        """Test loading admin emails from settings."""
        with override_settings(EXCHANGE_ADMIN_EMAILS="admin1@test.com,admin2@test.com"):
            service = ExchangeEmailNotificationService()
            assert service.admin_emails == ["admin1@test.com", "admin2@test.com"]

    @patch.object(EmailService, "send_email")
    def test_notify_submission(self, mock_send_email, notification_service, exchange):
        """Test submission notification."""
        mock_send_email.return_value = True
        exchange.status = "SUBMITTED"
        exchange.submission_date = timezone.now()
        exchange.save()

        result = notification_service.notify_submission(exchange)

        assert result is True
        # Should send 2 emails: one to student, one to admins
        assert mock_send_email.call_count == 2

        # Check student notification
        student_call = mock_send_email.call_args_list[0]
        assert student_call[1]["to_emails"] == ["john.doe@example.com"]
        assert "Submitted" in student_call[1]["subject"]
        assert student_call[1]["template_name"] == "exchange_submitted"

        # Check admin notification
        admin_call = mock_send_email.call_args_list[1]
        assert "New Exchange Application" in admin_call[1]["subject"]
        assert admin_call[1]["template_name"] == "exchange_submitted_admin"

    @patch.object(EmailService, "send_email")
    def test_notify_approval(self, mock_send_email, notification_service, exchange):
        """Test approval notification."""
        mock_send_email.return_value = True
        exchange.status = "APPROVED"
        exchange.save()

        result = notification_service.notify_approval(exchange)

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[1]
        assert call_args["to_emails"] == ["john.doe@example.com"]
        assert "Approved" in call_args["subject"]
        assert call_args["template_name"] == "exchange_approved"
        assert call_args["context"]["exchange"] == exchange

    @patch.object(EmailService, "send_email")
    def test_notify_rejection(self, mock_send_email, notification_service, exchange):
        """Test rejection notification."""
        mock_send_email.return_value = True
        exchange.status = "REJECTED"
        exchange.notes = "Insufficient GPA"
        exchange.save()

        result = notification_service.notify_rejection(exchange)

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[1]
        assert call_args["to_emails"] == ["john.doe@example.com"]
        assert "Update" in call_args["subject"]
        assert call_args["template_name"] == "exchange_rejected"
        assert call_args["context"]["reason"] == "Insufficient GPA"

    @patch.object(EmailService, "send_email")
    def test_notify_review_assigned(
        self, mock_send_email, notification_service, exchange, user
    ):
        """Test review assignment notification."""
        mock_send_email.return_value = True
        reviewer = User.objects.create_user(
            username="reviewer",
            email="reviewer@test.com",
            password="pass123",
            first_name="Jane",
            last_name="Reviewer",
        )
        exchange.reviewed_by = reviewer
        exchange.save()

        result = notification_service.notify_review_assigned(exchange, reviewer)

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[1]
        assert call_args["to_emails"] == ["reviewer@test.com"]
        assert "Review" in call_args["subject"]
        assert call_args["context"]["reviewer_name"] == "Jane Reviewer"

    @patch.object(EmailService, "send_email")
    def test_notify_document_uploaded_draft_status(
        self, mock_send_email, notification_service, exchange
    ):
        """Test that no notification is sent for document upload when status is DRAFT."""
        result = notification_service.notify_document_uploaded(
            exchange, "test_document.pdf"
        )

        assert result is True
        mock_send_email.assert_not_called()

    @patch.object(EmailService, "send_email")
    def test_notify_document_uploaded_submitted_status(
        self, mock_send_email, notification_service, exchange
    ):
        """Test notification for document upload when status is SUBMITTED."""
        with override_settings(EXCHANGE_ADMIN_EMAILS=["admin@test.com"]):
            notification_service.admin_emails = ["admin@test.com"]
            exchange.status = "SUBMITTED"
            exchange.save()

            mock_send_email.return_value = True
            result = notification_service.notify_document_uploaded(
                exchange, "test_document.pdf"
            )

            assert result is True
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args["to_emails"] == ["admin@test.com"]
            assert "Document Uploaded" in call_args["subject"]
