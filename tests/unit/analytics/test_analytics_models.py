import pytest
from django.contrib.auth import get_user_model

from analytics.models import DashboardConfig, Metric, Report

User = get_user_model()

@pytest.mark.django_db
class TestReport:
    def test_report_creation(self):
        """Test creating a Report instance."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        report = Report.objects.create(
            name='Test Report',
            description='A test report',
            created_by=user
        )
        assert report.name == 'Test Report'
        assert report.description == 'A test report'
        assert report.created_by == user
        assert str(report) == 'Test Report'

    def test_report_str_method(self):
        """Test the string representation of Report."""
        report = Report.objects.create(name='Test Report')
        assert str(report) == 'Test Report'

    def test_report_without_created_by(self):
        """Test creating a Report without a created_by user."""
        report = Report.objects.create(
            name='Anonymous Report',
            description='A report without creator'
        )
        assert report.created_by is None
        assert report.name == 'Anonymous Report'

@pytest.mark.django_db
class TestMetric:
    def test_metric_creation(self):
        """Test creating a Metric instance."""
        report = Report.objects.create(name='Test Report')
        metric = Metric.objects.create(
            name='test_metric',
            value=42.5,
            report=report
        )
        assert metric.name == 'test_metric'
        assert metric.value == 42.5
        assert metric.report == report
        assert str(metric) == 'test_metric: 42.5'

    def test_metric_str_method(self):
        """Test the string representation of Metric."""
        report = Report.objects.create(name='Test Report')
        metric = Metric.objects.create(
            name='test_metric',
            value=100.0,
            report=report
        )
        assert str(metric) == 'test_metric: 100.0'

    def test_metric_relationship(self):
        """Test the relationship between Metric and Report."""
        report = Report.objects.create(name='Test Report')
        metric1 = Metric.objects.create(name='metric1', value=10.0, report=report)
        metric2 = Metric.objects.create(name='metric2', value=20.0, report=report)

        assert report.metrics.count() == 2
        assert metric1 in report.metrics.all()
        assert metric2 in report.metrics.all()

@pytest.mark.django_db
class TestDashboardConfig:
    def test_dashboard_config_creation(self):
        """Test creating a DashboardConfig instance."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        config_data = {'widgets': ['chart1', 'chart2'], 'layout': 'grid'}

        dashboard_config = DashboardConfig.objects.create(
            user=user,
            config=config_data
        )
        assert dashboard_config.user == user
        assert dashboard_config.config == config_data
        assert str(dashboard_config) == f'Dashboard config for {user.username}'

    def test_dashboard_config_str_method(self):
        """Test the string representation of DashboardConfig."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        dashboard_config = DashboardConfig.objects.create(
            user=user,
            config={'test': 'config'}
        )
        assert str(dashboard_config) == f'Dashboard config for {user.username}'

    def test_dashboard_config_empty_config(self):
        """Test creating a DashboardConfig with empty config."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        dashboard_config = DashboardConfig.objects.create(
            user=user,
            config={}
        )
        assert dashboard_config.config == {}
