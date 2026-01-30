"""
Tests for Notification Center API and functionality.
"""

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from notifications.models import Notification


@pytest.mark.django_db
class TestNotificationCenterAPI:
    """Test Notification Center API endpoints."""
    
    def test_list_notifications(self, api_client_authenticated_student, notifications):
        """Test listing notifications."""
        response = api_client_authenticated_student.get('/api/notifications/')
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(notifications)
    
    def test_filter_unread_notifications(self, api_client_authenticated_student, notifications):
        """Test filtering for unread notifications only."""
        response = api_client_authenticated_student.get('/api/notifications/?unread=true')
        
        assert response.status_code == 200
        data = response.json()
        results = data['results']
        
        # Should only show unread
        assert all(not n['is_read'] for n in results)
    
    def test_filter_by_category(self, api_client_authenticated_student, notifications):
        """Test filtering notifications by category."""
        response = api_client_authenticated_student.get('/api/notifications/?category=success')
        
        assert response.status_code == 200
        data = response.json()
        results = data['results']
        
        assert all(n['category'] == 'success' for n in results)
    
    def test_mark_notification_read(self, api_client_authenticated_student, notifications):
        """Test marking a single notification as read."""
        notification = notifications[0]
        assert not notification.is_read
        
        response = api_client_authenticated_student.post(
            f'/api/notifications/{notification.id}/mark_read/'
        )
        
        assert response.status_code == 200
        
        # Verify in database
        notification.refresh_from_db()
        assert notification.is_read
    
    def test_mark_all_notifications_read(self, api_client_authenticated_student, notifications):
        """Test marking all notifications as read."""
        # Ensure some are unread
        unread_count = Notification.objects.filter(
            recipient=notifications[0].recipient,
            is_read=False
        ).count()
        assert unread_count > 0
        
        response = api_client_authenticated_student.post('/api/notifications/mark_all_read/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == unread_count
        
        # Verify all are read
        unread_after = Notification.objects.filter(
            recipient=notifications[0].recipient,
            is_read=False
        ).count()
        assert unread_after == 0
    
    def test_delete_notification(self, api_client_authenticated_student, notifications):
        """Test deleting a notification."""
        notification = notifications[0]
        notification_id = notification.id
        
        response = api_client_authenticated_student.delete(
            f'/api/notifications/{notification_id}/'
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        assert not Notification.objects.filter(id=notification_id).exists()
    
    def test_get_unread_count(self, api_client_authenticated_student, notifications):
        """Test getting unread notification count."""
        # Count unread in fixtures
        user = notifications[0].recipient
        expected_count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        response = api_client_authenticated_student.get('/api/notifications/unread_count/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['count'] == expected_count
    
    def test_user_only_sees_own_notifications(self, api_client_authenticated_student, other_user_notifications):
        """Test users can only see their own notifications."""
        response = api_client_authenticated_student.get('/api/notifications/')
        
        assert response.status_code == 200
        data = response.json()
        # Student shouldn't see other user's notifications
        assert len(data['results']) == 0
    
    def test_notifications_ordered_by_sent_at(self, api_client_authenticated_student, notifications):
        """Test notifications are ordered by sent_at descending."""
        response = api_client_authenticated_student.get('/api/notifications/')
        
        assert response.status_code == 200
        data = response.json()
        results = data['results']
        
        # Check ordering (most recent first)
        if len(results) > 1:
            dates = [n['sent_at'] for n in results]
            assert dates == sorted(dates, reverse=True)
    
    def test_notification_pagination(self, api_client_authenticated_student, many_notifications):
        """Test notification pagination."""
        response = api_client_authenticated_student.get('/api/notifications/?page=1')
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'results' in data
        assert 'count' in data
        assert 'next' in data or 'previous' in data


@pytest.mark.django_db
class TestNotificationService:
    """Test NotificationService with WebSocket integration."""
    
    def test_send_notification_with_category(self, user_student):
        """Test sending notification with category."""
        from notifications.services import NotificationService
        
        notification = NotificationService.send_notification(
            recipient=user_student,
            title="Test Success",
            message="Operation completed successfully",
            category="success"
        )
        
        assert notification.category == "success"
        assert notification.recipient == user_student
    
    def test_send_notification_with_action_url(self, user_student):
        """Test sending notification with action URL."""
        from notifications.services import NotificationService
        
        notification = NotificationService.send_notification(
            recipient=user_student,
            title="Application Updated",
            message="Your application has been reviewed",
            action_url="/applications/123/",
            action_text="View Application",
            category="info"
        )
        
        assert notification.action_url == "/applications/123/"
        assert notification.action_text == "View Application"
    
    def test_notification_broadcast_via_websocket(self, user_student):
        """Test notification is broadcast via WebSocket."""
        from notifications.services import NotificationService
        
        with patch('notifications.services.async_to_sync') as mock_async:
            with patch('notifications.services.get_channel_layer') as mock_channel_layer:
                mock_layer = Mock()
                mock_channel_layer.return_value = mock_layer
                
                notification = NotificationService.send_notification(
                    recipient=user_student,
                    title="Test Notification",
                    message="Test message",
                    category="info"
                )
                
                # Verify channel layer was called
                assert mock_async.called
                # Verify notification data was prepared correctly
                assert notification.title == "Test Notification"


@pytest.fixture
def notifications(user_student):
    """Create test notifications."""
    notifications_list = []
    
    categories = ['info', 'success', 'warning', 'error']
    
    for i, category in enumerate(categories):
        notif = Notification.objects.create(
            recipient=user_student,
            title=f"Test {category.title()} Notification",
            message=f"This is a {category} notification",
            category=category,
            is_read=i % 2 == 0  # Alternate read/unread
        )
        notifications_list.append(notif)
    
    return notifications_list


@pytest.fixture
def many_notifications(user_student):
    """Create many notifications for pagination testing."""
    notifications_list = []
    
    for i in range(30):
        notif = Notification.objects.create(
            recipient=user_student,
            title=f"Notification {i}",
            message=f"Message {i}",
            category='info',
            is_read=False
        )
        notifications_list.append(notif)
    
    return notifications_list


@pytest.fixture
def other_user_notifications(db):
    """Create notifications for another user."""
    from accounts.models import Role
    
    other_user = User.objects.create_user(
        username='other_user',
        email='other@test.com',
        password='testpass123'
    )
    
    notifications_list = []
    
    for i in range(3):
        notif = Notification.objects.create(
            recipient=other_user,
            title=f"Other User Notification {i}",
            message=f"Message {i}",
            category='info',
            is_read=False
        )
        notifications_list.append(notif)
    
    return notifications_list


@pytest.fixture
def api_client_authenticated_student(user_student):
    """Create authenticated API client for student."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user_student)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client

