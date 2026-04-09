"""
Tests for Calendar Events API.
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from exchange.calendar_ics import sign_calendar_subscribe_token
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.mark.django_db
class TestCalendarEventAPI:
    """Test Calendar Events API."""
    
    def test_get_calendar_events(self, api_client_authenticated_student, calendar_programs):
        """Test getting calendar events."""
        response = api_client_authenticated_student.get('/api/calendar/events/')
        
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        assert len(events) > 0
    
    def test_calendar_events_format(self, api_client_authenticated_student, calendar_programs):
        """Test calendar events are in FullCalendar format."""
        response = api_client_authenticated_student.get('/api/calendar/events/')
        
        assert response.status_code == 200
        events = response.json()
        
        # Check FullCalendar format
        for event in events:
            assert 'id' in event
            assert 'title' in event
            assert 'start' in event
            # Optional fields (DRF may include url as null)
            if event.get("url") is not None:
                assert isinstance(event["url"], str)
            if event.get("spa_path") is not None:
                assert isinstance(event["spa_path"], str)
    
    def test_filter_by_date_range(self, api_client_authenticated_student, calendar_programs):
        """Test filtering events by date range."""
        start = timezone.now()
        end = start + timedelta(days=90)
        
        response = api_client_authenticated_student.get(
            f'/api/calendar/events/?start={start.isoformat()}&end={end.isoformat()}'
        )
        
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
    
    def test_filter_by_event_type_program(self, api_client_authenticated_student, calendar_programs):
        """Test filtering events by type: program."""
        response = api_client_authenticated_student.get('/api/calendar/events/?type=program')
        
        assert response.status_code == 200
        events = response.json()
        
        # All events should be program-related
        assert all('program' in event['id'] for event in events)
    
    def test_filter_by_event_type_application(self, api_client_authenticated_student, student_applications):
        """Test filtering events by type: application."""
        response = api_client_authenticated_student.get('/api/calendar/events/?type=application')
        
        assert response.status_code == 200
        events = response.json()
        
        # All events should be application-related
        assert all('application' in event['id'] for event in events)
    
    def test_student_sees_only_own_applications(self, api_client_authenticated_student, student_applications, other_student_applications):
        """Test students only see their own application events."""
        response = api_client_authenticated_student.get('/api/calendar/events/?type=application')
        
        assert response.status_code == 200
        events = response.json()
        
        # Should only see own applications
        own_app_ids = [str(app.id) for app in student_applications]
        event_ids = [e['id'].replace('application-', '') for e in events]
        
        assert all(eid in own_app_ids for eid in event_ids)
    
    def test_coordinator_sees_all_applications(self, api_client_authenticated_coordinator, student_applications, other_student_applications):
        """Test coordinators see all application events."""
        response = api_client_authenticated_coordinator.get('/api/calendar/events/?type=application')
        
        assert response.status_code == 200
        events = response.json()
        
        # Should see all applications
        total_apps = len(student_applications) + len(other_student_applications)
        assert len(events) == total_apps
    
    def test_program_start_end_events(self, api_client_authenticated_student, calendar_programs):
        """Test program start and end events are generated."""
        response = api_client_authenticated_student.get('/api/calendar/events/?type=program')
        
        assert response.status_code == 200
        events = response.json()
        
        # Should have both start and end events for each program
        start_events = [e for e in events if 'start' in e['id']]
        end_events = [e for e in events if 'end' in e['id']]
        
        assert len(start_events) > 0
        assert len(end_events) > 0

    def test_subscribe_token_authenticated(self, api_client_authenticated_student):
        response = api_client_authenticated_student.get(
            "/api/calendar/events/subscribe-token/"
        )
        assert response.status_code == 200
        data = response.json()
        assert "ics_url" in data and "webcal_url" in data
        assert "/api/calendar/subscribe.ics" in data["ics_url"]
        assert "token=" in data["ics_url"]
        assert data["webcal_url"].startswith("webcal://")

    def test_subscribe_ics_valid_token(self, student_user, calendar_programs):
        token = sign_calendar_subscribe_token(student_user.pk)
        client = APIClient()
        response = client.get("/api/calendar/subscribe.ics", {"token": token})
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/calendar")
        body = response.content.decode()
        assert "BEGIN:VCALENDAR" in body
        assert "END:VCALENDAR" in body

    def test_subscribe_ics_invalid_token(self):
        client = APIClient()
        response = client.get("/api/calendar/subscribe.ics", {"token": "not-valid"})
        assert response.status_code == 403

    def test_subscribe_ics_student_only_own_applications(
        self,
        student_user,
        student_applications,
        other_student_applications,
        calendar_programs,
    ):
        token = sign_calendar_subscribe_token(student_user.pk)
        client = APIClient()
        response = client.get("/api/calendar/subscribe.ics", {"token": token})
        assert response.status_code == 200
        body = response.content.decode()
        for app in student_applications:
            assert f"application-{app.id}@seim-calendar" in body
        for app in other_student_applications:
            assert f"application-{app.id}@seim-calendar" not in body


@pytest.mark.django_db
class TestReminderAPI:
    """Test Reminder API endpoints."""
    
    def test_create_reminder(self, api_client_authenticated_student, calendar_programs):
        """Test creating a reminder."""
        program = calendar_programs[0]
        remind_at = timezone.now() + timedelta(days=7)
        
        response = api_client_authenticated_student.post('/api/reminders/', {
            'event_type': 'program_start',
            'event_id': str(program.id),
            'event_title': f'Program Start: {program.name}',
            'remind_at': remind_at.isoformat()
        }, format='json')
        
        assert response.status_code == 201
        data = response.json()
        assert data['event_type'] == 'program_start'
        assert data['sent'] is False
    
    def test_list_reminders(self, api_client_authenticated_student, reminders):
        """Test listing reminders."""
        response = api_client_authenticated_student.get('/api/reminders/')
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(reminders)
    
    def test_get_upcoming_reminders(self, api_client_authenticated_student, reminders):
        """Test getting upcoming (unsent) reminders."""
        response = api_client_authenticated_student.get('/api/reminders/upcoming/')
        
        assert response.status_code == 200
        reminders_list = response.json()
        
        # Should only show unsent reminders
        assert all(not r['sent'] for r in reminders_list)
    
    def test_delete_reminder(self, api_client_authenticated_student, reminders):
        """Test deleting a reminder."""
        reminder = reminders[0]
        
        response = api_client_authenticated_student.delete(f'/api/reminders/{reminder.id}/')
        
        assert response.status_code == 204
        
        # Verify deleted
        from notifications.models import Reminder
        assert not Reminder.objects.filter(id=reminder.id).exists()
    
    def test_user_can_only_see_own_reminders(self, api_client_authenticated_student, other_user_reminders):
        """Test users can only see their own reminders."""
        response = api_client_authenticated_student.get('/api/reminders/')
        
        assert response.status_code == 200
        data = response.json()
        # Student shouldn't see other user's reminders
        assert len(data['results']) == 0
    
    def test_filter_reminders_by_event_type(self, api_client_authenticated_student, reminders):
        """Test filtering reminders by event type."""
        response = api_client_authenticated_student.get(
            '/api/reminders/?event_type=program_start'
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data['results']
        assert all(r['event_type'] == 'program_start' for r in results)


@pytest.mark.django_db
class TestReminderTask:
    """Test reminder sending task."""
    
    def test_send_deadline_reminders_task(self, student_user, calendar_programs):
        """Test the Celery task sends reminders."""
        from notifications.models import Reminder
        from notifications.tasks import send_deadline_reminders
        
        # Create a reminder that's due
        program = calendar_programs[0]
        reminder = Reminder.objects.create(
            user=student_user,
            event_type='program_start',
            event_id=program.id,
            event_title=f'Program Start: {program.name}',
            remind_at=timezone.now() - timedelta(minutes=5),  # Past due
            sent=False
        )
        
        # Run task
        count = send_deadline_reminders()
        
        assert count == 1
        
        # Verify reminder was sent
        reminder.refresh_from_db()
        assert reminder.sent
        assert reminder.notification is not None
    
    def test_only_sends_unsent_reminders(self, student_user, calendar_programs):
        """Test task only sends unsent reminders."""
        from notifications.models import Reminder
        from notifications.tasks import send_deadline_reminders
        
        program = calendar_programs[0]
        
        # Create already sent reminder
        sent_reminder = Reminder.objects.create(
            user=student_user,
            event_type='program_start',
            event_id=program.id,
            event_title=f'Program Start: {program.name}',
            remind_at=timezone.now() - timedelta(days=1),
            sent=True
        )
        
        # Run task
        count = send_deadline_reminders()
        
        # Should not send again
        assert count == 0
    
    def test_only_sends_due_reminders(self, student_user, calendar_programs):
        """Test task only sends reminders that are due."""
        from notifications.models import Reminder
        from notifications.tasks import send_deadline_reminders
        
        program = calendar_programs[0]
        
        # Create future reminder
        future_reminder = Reminder.objects.create(
            user=student_user,
            event_type='program_start',
            event_id=program.id,
            event_title=f'Program Start: {program.name}',
            remind_at=timezone.now() + timedelta(days=7),  # Future
            sent=False
        )
        
        # Run task
        count = send_deadline_reminders()
        
        # Should not send yet
        assert count == 0
        
        future_reminder.refresh_from_db()
        assert not future_reminder.sent


@pytest.fixture
def calendar_programs(db):
    """Create test programs for calendar."""
    programs = []
    
    programs.append(Program.objects.create(
        name="Summer Exchange",
        description="Summer program",
        start_date=timezone.now().date() + timedelta(days=60),
        end_date=timezone.now().date() + timedelta(days=150),
        is_active=True
    ))
    
    programs.append(Program.objects.create(
        name="Fall Semester",
        description="Fall semester abroad",
        start_date=timezone.now().date() + timedelta(days=120),
        end_date=timezone.now().date() + timedelta(days=270),
        is_active=True
    ))
    
    return programs


@pytest.fixture
def student_applications(student_user, calendar_programs):
    """Create test applications for student."""
    apps = []
    status = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 1})[0]
    
    for program in calendar_programs:
        app = Application.objects.create(
            student=student_user,
            program=program,
            status=status,
            submitted_at=timezone.now()
        )
        apps.append(app)
    
    return apps


@pytest.fixture
def other_student_applications(db, calendar_programs):
    """Create applications for another student."""
    from accounts.models import Role
    
    other_user = User.objects.create_user(
        username='other_student',
        email='other@test.com',
        password='testpass123'
    )
    student_role = Role.objects.get_or_create(name='student')[0]
    other_user.roles.add(student_role)
    
    apps = []
    status = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 1})[0]
    
    for program in calendar_programs:
        app = Application.objects.create(
            student=other_user,
            program=program,
            status=status,
            submitted_at=timezone.now()
        )
        apps.append(app)
    
    return apps


@pytest.fixture
def reminders(student_user, calendar_programs):
    """Create test reminders."""
    from notifications.models import Reminder
    
    reminders_list = []
    
    for program in calendar_programs:
        reminder = Reminder.objects.create(
            user=student_user,
            event_type='program_start',
            event_id=program.id,
            event_title=f'Program Start: {program.name}',
            remind_at=timezone.now() + timedelta(days=7),
            sent=False
        )
        reminders_list.append(reminder)
    
    return reminders_list


@pytest.fixture
def other_user_reminders(db, calendar_programs):
    """Create reminders for another user."""
    from accounts.models import Role
    from notifications.models import Reminder
    
    other_user = User.objects.create_user(
        username='other_user',
        email='other2@test.com',
        password='testpass123'
    )
    
    reminders_list = []
    program = calendar_programs[0]
    
    reminder = Reminder.objects.create(
        user=other_user,
        event_type='program_start',
        event_id=program.id,
        event_title=f'Program Start: {program.name}',
        remind_at=timezone.now() + timedelta(days=7),
        sent=False
    )
    reminders_list.append(reminder)
    
    return reminders_list


@pytest.fixture
def api_client_authenticated_coordinator(coordinator_user):
    """Create authenticated API client for coordinator."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(coordinator_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client


@pytest.fixture
def api_client_authenticated_student(student_user):
    """Create authenticated API client for student."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(student_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client

