"""
Comprehensive test suite for exchange workflow functionality
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from exchange.models import Exchange, UserProfile, WorkflowLog
from exchange.services.workflow import WorkflowService
from exchange.forms import ExchangeForm


class ExchangeWorkflowTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.student = User.objects.create_user(
            username='student', 
            email='student@test.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            first_name='Jane', 
            last_name='Smith',
            password='testpass123',
            is_staff=True
        )
        
        # Create user profiles
        self.student_profile = UserProfile.objects.create(
            user=self.student,
            role='STUDENT',
            student_id='STU123456',
            phone='555-0123',
            institution='Test University'
        )
        
        self.coordinator_profile = UserProfile.objects.create(
            user=self.coordinator,
            role='COORDINATOR'
        )
        
        # Create groups and assign permissions
        coordinator_group = Group.objects.create(name='Exchange Coordinators')
        self.coordinator.groups.add(coordinator_group)
    
    def test_exchange_creation_view(self):
        """Test exchange application creation"""
        self.client.login(username='student', password='testpass123')
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@test.com',
            'student_number': 'STU123456',
            'current_university': 'Test University',
            'current_program': 'Computer Science',
            'destination_university': 'Partner University',
            'destination_country': 'USA',
            'exchange_program': 'Semester Exchange',
            'start_date': (date.today() + timedelta(days=30)).isoformat(),
            'end_date': (date.today() + timedelta(days=180)).isoformat(),
            'motivation_letter': 'This is my motivation letter for the exchange program. ' * 20,
            'action': 'submit'
        }
        
        response = self.client.post(reverse('exchange:create-exchange'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check that exchange was created
        exchange = Exchange.objects.get(student=self.student)
        self.assertEqual(exchange.status, 'SUBMITTED')
        self.assertIsNotNone(exchange.submission_date)
        self.assertEqual(exchange.first_name, 'John')
        self.assertEqual(exchange.last_name, 'Doe')
    
    def test_exchange_approval_workflow(self):
        """Test exchange application approval"""
        # Create exchange
        exchange = Exchange.objects.create(
            student=self.student,
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com',
            student_number='STU123456',
            current_university='Test University',
            current_program='Computer Science', 
            destination_university='Partner University',
            destination_country='USA',
            exchange_program='Semester Exchange',
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            motivation_letter='This is my motivation letter. ' * 20,
            status='SUBMITTED',
            submission_date=timezone.now()
        )
        
        # Login as coordinator
        self.client.login(username='coordinator', password='testpass123')
        
        # Approve exchange
        response = self.client.post(
            reverse('exchange:approve-exchange', args=[exchange.id]),
            {'comment': 'Application looks good'}
        )
        
        self.assertEqual(response.status_code, 302)
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, 'APPROVED')
    
    def test_exchange_rejection_workflow(self):
        """Test exchange application rejection"""
        # Create exchange
        exchange = Exchange.objects.create(
            student=self.student,
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com',
            student_number='STU123456',
            status='SUBMITTED',
            submission_date=timezone.now()
        )
        
        # Login as coordinator
        self.client.login(username='coordinator', password='testpass123')
        
        # Reject exchange
        response = self.client.post(
            reverse('exchange:reject-exchange', args=[exchange.id]),
            {'comment': 'Missing required documents'}
        )
        
        self.assertEqual(response.status_code, 302)
        exchange.refresh_from_db()
        self.assertEqual(exchange.status, 'REJECTED')
