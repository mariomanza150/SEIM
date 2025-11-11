from django.contrib.auth import get_user_model
from django.test import TestCase

from analytics import serializers
from analytics.models import Report

User = get_user_model()

class TestAnalyticsSerializers(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.report = Report.objects.create(
            name='Test Report',
            description='Test Description',
            created_by=self.user
        )

    def test_metric_serializer_valid(self):
        """Test metric serializer with valid data"""
        data = {
            'name': 'test_metric',
            'value': 100.0,
            'report': self.report.id
        }
        serializer = serializers.MetricSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_metric_serializer_missing_fields(self):
        """Test metric serializer with missing required fields"""
        data = {'name': 'test_metric'}
        serializer = serializers.MetricSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)
        self.assertIn('report', serializer.errors)

    def test_metric_serializer_invalid_value(self):
        """Test metric serializer with invalid value"""
        data = {
            'name': 'test_metric',
            'value': 'not_a_number',
            'report': self.report.id
        }
        serializer = serializers.MetricSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)

    def test_report_serializer_valid(self):
        """Test report serializer with valid data"""
        data = {
            'name': 'Test Report',
            'description': 'Test Description',
            'created_by': self.user.id
        }
        serializer = serializers.ReportSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_report_serializer_missing_name(self):
        """Test report serializer with missing name"""
        data = {
            'description': 'Test Description',
            'created_by': self.user.id
        }
        serializer = serializers.ReportSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_dashboard_config_serializer_valid(self):
        """Test dashboard config serializer with valid data"""
        data = {
            'user': self.user.id,
            'config': {'widgets': [], 'layout': 'grid'}
        }
        serializer = serializers.DashboardConfigSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_dashboard_config_serializer_invalid_config(self):
        """Test dashboard config serializer with invalid config"""
        data = {
            'user': self.user.id,
            'config': None  # Use None instead of string to trigger validation error
        }
        serializer = serializers.DashboardConfigSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('config', serializer.errors)
