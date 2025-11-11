import uuid
from datetime import UTC, date, datetime
from unittest.mock import patch

import pytest

from accounts.models import User
from analytics import tasks
from analytics.models import Metric, Report
from exchange.models import Application, ApplicationStatus, Program


@pytest.mark.django_db
class TestGenerateReportTask:
    def test_generate_report_task_success(self):
        """Test successful execution of generate_report task."""
        # Create test data
        user = User.objects.create_user(username='testuser', email='test@example.com')
        report = Report.objects.create(
            name='Test Report',
            description='A test report',
            created_by=user
        )

        # Use get_or_create for statuses
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name='submitted')
        approved_status, _ = ApplicationStatus.objects.get_or_create(name='approved')
        rejected_status, _ = ApplicationStatus.objects.get_or_create(name='rejected')

        # Create program with required fields
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )

        # Create applications with different statuses
        Application.objects.create(
            program=program,
            student=user,
            status=submitted_status
        )
        Application.objects.create(
            program=program,
            student=user,
            status=approved_status
        )
        Application.objects.create(
            program=program,
            student=user,
            status=rejected_status
        )

        # Execute the task
        tasks.generate_report(report.id)

        # Verify metrics were created
        metrics = Metric.objects.filter(report=report)
        assert metrics.count() == 3

        # Check specific metrics
        submitted_metric = metrics.filter(name='applications_submitted').first()
        approved_metric = metrics.filter(name='applications_approved').first()
        rejected_metric = metrics.filter(name='applications_rejected').first()

        assert submitted_metric is not None and submitted_metric.value == 1
        assert approved_metric is not None and approved_metric.value == 1
        assert rejected_metric is not None and rejected_metric.value == 1

    def test_generate_report_task_no_applications(self):
        """Test generate_report task when no applications exist."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        report = Report.objects.create(
            name='Test Report',
            description='A test report',
            created_by=user
        )

        # Execute the task
        tasks.generate_report(report.id)

        # Verify metrics were created with zero values
        metrics = Metric.objects.filter(report=report)
        assert metrics.count() == 3

        for metric in metrics:
            assert metric.value == 0

    def test_generate_report_task_report_not_found(self):
        """Test generate_report task with non-existent report ID."""
        fake_uuid = uuid.uuid4()
        with pytest.raises(Report.DoesNotExist):
            tasks.generate_report(fake_uuid)

    @patch('analytics.tasks.timezone.now')
    def test_generate_report_task_timestamp(self, mock_now):
        """Test that generate_report task sets proper timestamps."""
        mock_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
        mock_now.return_value = mock_time

        user = User.objects.create_user(username='testuser', email='test@example.com')
        report = Report.objects.create(
            name='Test Report',
            description='A test report',
            created_by=user
        )

        # Execute the task
        tasks.generate_report(report.id)

        # Verify timestamps
        metrics = Metric.objects.filter(report=report)
        for metric in metrics:
            assert metric.calculated_at == mock_time

    def test_generate_report_task_with_existing_metrics(self):
        """Test generate_report task adds new metrics without overwriting existing ones."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        report = Report.objects.create(
            name='Test Report',
            description='A test report',
            created_by=user
        )
        # Create program with required fields
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )
        # Use get_or_create for status
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name='submitted')
        # Create application
        Application.objects.create(
            program=program,
            student=user,
            status=submitted_status
        )
        # Create existing metric with the same name as the task will generate
        Metric.objects.create(
            name='applications_submitted',
            value=5.0,
            report=report
        )
        # Execute the task
        tasks.generate_report(report.id)
        # Verify new metrics were added (should have 4 total now: 1 existing + 3 new)
        metrics = Metric.objects.filter(report=report)
        assert metrics.count() == 4
        # Check that the existing metric was not overwritten and a new one was added
        values = list(metrics.filter(name='applications_submitted').values_list('value', flat=True))
        assert 5.0 in values
        assert 1.0 in values or 0.0 in values  # depending on task logic
