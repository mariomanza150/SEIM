"""
Tests for Exchange filters.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from ..filters import ExchangeFilter
from ..models import Exchange


@pytest.mark.django_db
class TestExchangeFilter:
    """Test suite for ExchangeFilter."""

    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @pytest.fixture
    def exchanges(self, user):
        """Create test exchanges."""
        exchanges = []

        # Create multiple exchanges with different data
        exchange1 = Exchange.objects.create(
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
            status="SUBMITTED",
            submission_date=timezone.now(),
        )
        exchanges.append(exchange1)

        exchange2 = Exchange.objects.create(
            student=user,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            student_id="STU002",
            current_university="Test University",
            current_program="Business Administration",
            current_year=2,
            gpa=Decimal("3.8"),
            destination_university="Cambridge",
            destination_country="UK",
            exchange_program="Exchange Program B",
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=210),
            status="APPROVED",
            submission_date=timezone.now() - timedelta(days=10),
        )
        exchanges.append(exchange2)

        exchange3 = Exchange.objects.create(
            student=user,
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            student_id="STU003",
            current_university="Another University",
            current_program="Engineering",
            current_year=4,
            gpa=Decimal("3.2"),
            destination_university="Tokyo University",
            destination_country="Japan",
            exchange_program="Exchange Program C",
            start_date=date.today() + timedelta(days=90),
            end_date=date.today() + timedelta(days=240),
            status="DRAFT",
        )
        exchanges.append(exchange3)

        return exchanges

    def test_status_filter(self, exchanges):
        """Test filtering by status."""
        filter_set = ExchangeFilter(
            {"status": "SUBMITTED"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().status == "SUBMITTED"

    def test_date_range_filters(self, exchanges):
        """Test date range filtering."""
        # Test submission date range
        filter_set = ExchangeFilter(
            {
                "submission_date_from": (timezone.now() - timedelta(days=15)).date(),
                "submission_date_to": timezone.now().date(),
            },
            queryset=Exchange.objects.all(),
        )

        # Should get exchange1 only (submitted today)
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().first_name == "John"

    def test_student_info_filters(self, exchanges):
        """Test filtering by student information."""
        # Test first name filter
        filter_set = ExchangeFilter(
            {"first_name": "Jane"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().first_name == "Jane"

        # Test email filter (partial match)
        filter_set = ExchangeFilter({"email": "smith"}, queryset=Exchange.objects.all())
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().email == "jane.smith@example.com"

    def test_academic_filters(self, exchanges):
        """Test academic information filters."""
        # Test GPA range
        filter_set = ExchangeFilter(
            {"gpa_min": "3.4", "gpa_max": "3.9"}, queryset=Exchange.objects.all()
        )

        # Should get exchanges with GPA 3.5 and 3.8
        assert filter_set.qs.count() == 2

        # Test current year
        filter_set = ExchangeFilter(
            {"current_year": 3}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().current_year == 3

    def test_destination_filters(self, exchanges):
        """Test destination filters."""
        # Test destination country
        filter_set = ExchangeFilter(
            {"destination_country": "USA"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().destination_country == "USA"

        # Test destination university (partial match)
        filter_set = ExchangeFilter(
            {"destination_university": "Cambridge"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1

    def test_full_text_search(self, exchanges):
        """Test full-text search across multiple fields."""
        # Search for 'MIT' should find exchange1
        filter_set = ExchangeFilter({"search": "MIT"}, queryset=Exchange.objects.all())
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().destination_university == "MIT"

        # Search for 'Engineering' should find exchange3
        filter_set = ExchangeFilter(
            {"search": "Engineering"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 1
        assert filter_set.qs.first().current_program == "Engineering"

        # Search for email domain
        filter_set = ExchangeFilter(
            {"search": "@example.com"}, queryset=Exchange.objects.all()
        )
        assert filter_set.qs.count() == 3  # All have @example.com

    def test_ordering(self, exchanges):
        """Test ordering functionality."""
        # Order by GPA descending
        filter_set = ExchangeFilter(
            {"ordering": "-gpa"}, queryset=Exchange.objects.all()
        )
        ordered_qs = list(filter_set.qs)
        assert ordered_qs[0].gpa == Decimal("3.8")  # Jane
        assert ordered_qs[1].gpa == Decimal("3.5")  # John
        assert ordered_qs[2].gpa == Decimal("3.2")  # Bob

        # Order by submission date
        filter_set = ExchangeFilter(
            {"ordering": "submission_date"}, queryset=Exchange.objects.all()
        )
        ordered_qs = list(filter_set.qs)
        # Bob has no submission date (NULL), Jane submitted 10 days ago, John today
        assert ordered_qs[0].first_name == "Bob"  # NULL first
        assert ordered_qs[1].first_name == "Jane"
        assert ordered_qs[2].first_name == "John"

    def test_combined_filters(self, exchanges):
        """Test combining multiple filters."""
        filter_set = ExchangeFilter(
            {"status": "APPROVED", "gpa_min": "3.5", "destination_country": "UK"},
            queryset=Exchange.objects.all(),
        )

        # Should only get Jane's exchange
        assert filter_set.qs.count() == 1
        result = filter_set.qs.first()
        assert result.first_name == "Jane"
        assert result.status == "APPROVED"
        assert result.gpa == Decimal("3.8")
        assert result.destination_country == "UK"

    def test_empty_filters(self, exchanges):
        """Test with no filters applied."""
        filter_set = ExchangeFilter({}, queryset=Exchange.objects.all())
        # Should return all exchanges
        assert filter_set.qs.count() == 3
