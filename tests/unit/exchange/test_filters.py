"""
Tests for advanced search filters.
"""

import pytest
from django.utils import timezone
from datetime import timedelta

from exchange.filters import ApplicationFilter, ProgramFilter
from exchange.models import Application, ApplicationStatus, Program
from accounts.models import User


@pytest.mark.django_db
class TestProgramFilter:
    """Test ProgramFilter functionality."""
    
    def test_filter_by_name(self, programs):
        """Test filtering programs by name."""
        filterset = ProgramFilter(
            data={'name': 'Erasmus'},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert len(results) > 0
        assert all('erasmus' in p.name.lower() for p in results)
    
    def test_filter_by_active_status(self, programs):
        """Test filtering by active status."""
        filterset = ProgramFilter(
            data={'is_active': True},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(p.is_active for p in results)
    
    def test_filter_by_date_range(self, programs):
        """Test filtering by date range."""
        future_date = timezone.now().date() + timedelta(days=30)
        
        filterset = ProgramFilter(
            data={'start_date_after': future_date.isoformat()},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(p.start_date >= future_date for p in results)
    
    def test_filter_by_gpa(self, programs):
        """Test filtering by GPA requirement."""
        filterset = ProgramFilter(
            data={'min_gpa_max': 3.0},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        # Results should only include programs with GPA <= 3.0 or None
        assert all(p.min_gpa is None or p.min_gpa <= 3.0 for p in results)
    
    def test_filter_by_language(self, programs):
        """Test filtering by required language."""
        filterset = ProgramFilter(
            data={'required_language': 'English'},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all('english' in (p.required_language or '').lower() for p in results)
    
    def test_search_full_text(self, programs):
        """Test full-text search across name and description."""
        filterset = ProgramFilter(
            data={'search': 'exchange'},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        # Should find programs with 'exchange' in name or description
        assert len(results) > 0
    
    def test_ordering(self, programs):
        """Test ordering by different fields."""
        filterset = ProgramFilter(
            data={'ordering': 'start_date'},
            queryset=Program.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        # Verify order
        dates = [p.start_date for p in results]
        assert dates == sorted(dates)


@pytest.mark.django_db
class TestApplicationFilter:
    """Test ApplicationFilter functionality."""
    
    def test_filter_by_student_name(self, applications):
        """Test filtering by student name."""
        student = applications[0].student
        
        filterset = ApplicationFilter(
            data={'student_name': student.username},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(
            student.username.lower() in a.student.username.lower() or
            student.username.lower() in (a.student.first_name or '').lower() or
            student.username.lower() in (a.student.last_name or '').lower()
            for a in results
        )
    
    def test_filter_by_student_email(self, applications):
        """Test filtering by student email."""
        student = applications[0].student
        
        filterset = ApplicationFilter(
            data={'student_email': student.email},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(student.email.lower() in a.student.email.lower() for a in results)
    
    def test_filter_by_program_name(self, applications):
        """Test filtering by program name."""
        program = applications[0].program
        
        filterset = ApplicationFilter(
            data={'program_name': program.name},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(program.name.lower() in a.program.name.lower() for a in results)
    
    def test_filter_by_status(self, applications):
        """Test filtering by application status."""
        status = applications[0].status
        
        filterset = ApplicationFilter(
            data={'status_name': status.name},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(a.status.name == status.name for a in results)
    
    def test_filter_by_submitted_date(self, applications):
        """Test filtering by submission date."""
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        
        filterset = ApplicationFilter(
            data={'submitted_after': yesterday.isoformat()},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(
            a.submitted_at is None or a.submitted_at >= yesterday
            for a in results
        )
    
    def test_filter_active_applications(self, applications):
        """Test filtering active (not withdrawn) applications."""
        filterset = ApplicationFilter(
            data={'active': True},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(not a.withdrawn for a in results)
    
    def test_search_multiple_fields(self, applications):
        """Test search across multiple fields."""
        student = applications[0].student
        
        filterset = ApplicationFilter(
            data={'search': student.username[:5]},
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert len(results) > 0
    
    def test_multiple_filters_combined(self, applications):
        """Test combining multiple filters."""
        program = applications[0].program
        status = applications[0].status
        
        filterset = ApplicationFilter(
            data={
                'program_name': program.name,
                'status_name': status.name,
                'withdrawn': False
            },
            queryset=Application.objects.all()
        )
        
        assert filterset.is_valid()
        results = list(filterset.qs)
        assert all(
            a.program.name == program.name and
            a.status.name == status.name and
            not a.withdrawn
            for a in results
        )


@pytest.fixture
def programs(db):
    """Create test programs."""
    programs_list = []
    
    # Create diverse programs for testing
    programs_list.append(Program.objects.create(
        name="Erasmus+ Europe",
        description="Exchange program to European universities",
        start_date=timezone.now().date() + timedelta(days=60),
        end_date=timezone.now().date() + timedelta(days=240),
        is_active=True,
        min_gpa=3.0,
        required_language="English",
        min_language_level="B2"
    ))
    
    programs_list.append(Program.objects.create(
        name="Study Abroad Asia",
        description="Experience Asian culture and education",
        start_date=timezone.now().date() + timedelta(days=90),
        end_date=timezone.now().date() + timedelta(days=270),
        is_active=True,
        min_gpa=2.5
    ))
    
    programs_list.append(Program.objects.create(
        name="Past Program",
        description="Already completed program",
        start_date=timezone.now().date() - timedelta(days=180),
        end_date=timezone.now().date() - timedelta(days=1),
        is_active=False
    ))
    
    return programs_list


@pytest.fixture
def applications(db, user_student, programs):
    """Create test applications."""
    apps = []
    
    draft_status = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 0})[0]
    submitted_status = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 1})[0]
    
    for i, program in enumerate(programs[:2]):
        app = Application.objects.create(
            student=user_student,
            program=program,
            status=draft_status if i == 0 else submitted_status,
            submitted_at=timezone.now() if i == 1 else None
        )
        apps.append(app)
    
    return apps

