"""
Integration tests for WebSocket notifications.

Tests WebSocket connection, notification broadcasting, and real-time updates.
"""

import json
import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from notifications.consumers import NotificationConsumer
from notifications.services import NotificationService
from notifications.models import Notification

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestWebSocketNotifications:
    """Test WebSocket notification functionality."""

    async def test_websocket_connect_authenticated(self):
        """Test that authenticated users can connect to WebSocket."""
        # Create test user
        user = await User.objects.acreate(
            username='testuser',
            email='test@example.com'
        )
        
        # Create WebSocket communicator
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        # Test connection
        connected, subprotocol = await communicator.connect()
        assert connected is True
        
        # Check connection confirmation message
        response = await communicator.receive_json_from()
        assert response['type'] == 'connection_established'
        assert 'user_id' in response
        
        # Close connection
        await communicator.disconnect()

    async def test_websocket_connect_unauthenticated(self):
        """Test that unauthenticated users cannot connect to WebSocket."""
        from django.contrib.auth.models import AnonymousUser
        
        # Create WebSocket communicator with anonymous user
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = AnonymousUser()
        
        # Test connection - should be rejected
        connected, subprotocol = await communicator.connect()
        assert connected is False

    async def test_notification_broadcast(self):
        """Test that notifications are broadcast to connected clients."""
        # Create test user
        user = await User.objects.acreate(
            username='testuser2',
            email='test2@example.com'
        )
        
        # Connect to WebSocket
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Receive connection confirmation
        await communicator.receive_json_from()
        
        # Send a notification (this will trigger broadcast)
        notification = await Notification.objects.acreate(
            recipient=user,
            title='Test Notification',
            message='This is a test notification',
            category='info'
        )
        
        # Manually broadcast (in real app, NotificationService does this)
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"notifications_{user.id}",
            {
                'type': 'notification_new',
                'notification': {
                    'id': str(notification.id),
                    'title': notification.title,
                    'message': notification.message,
                    'category': notification.category,
                    'action_url': None,
                    'action_text': 'View Details',
                    'sent_at': notification.sent_at.isoformat(),
                    'is_read': notification.is_read,
                }
            }
        )
        
        # Receive notification via WebSocket
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] == 'notification.new'
        assert response['notification']['title'] == 'Test Notification'
        assert response['notification']['message'] == 'This is a test notification'
        
        # Close connection
        await communicator.disconnect()

    async def test_mark_notification_read_via_websocket(self):
        """Test marking notification as read via WebSocket."""
        # Create test user and notification
        user = await User.objects.acreate(
            username='testuser3',
            email='test3@example.com'
        )
        
        notification = await Notification.objects.acreate(
            recipient=user,
            title='Test Notification',
            message='Test message',
            is_read=False
        )
        
        # Connect to WebSocket
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Receive connection confirmation
        await communicator.receive_json_from()
        
        # Send mark_read message
        await communicator.send_json_to({
            'type': 'mark_read',
            'notification_id': str(notification.id)
        })
        
        # Receive confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'notification_marked_read'
        assert response['notification_id'] == str(notification.id)
        
        # Verify notification is marked as read in database
        await notification.arefresh_from_db()
        assert notification.is_read is True
        
        # Close connection
        await communicator.disconnect()

    async def test_mark_all_notifications_read_via_websocket(self):
        """Test marking all notifications as read via WebSocket."""
        # Create test user and multiple notifications
        user = await User.objects.acreate(
            username='testuser4',
            email='test4@example.com'
        )
        
        # Create 3 unread notifications
        for i in range(3):
            await Notification.objects.acreate(
                recipient=user,
                title=f'Test Notification {i}',
                message=f'Test message {i}',
                is_read=False
            )
        
        # Connect to WebSocket
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Receive connection confirmation
        await communicator.receive_json_from()
        
        # Send mark_all_read message
        await communicator.send_json_to({
            'type': 'mark_all_read'
        })
        
        # Receive confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'all_notifications_marked_read'
        assert response['count'] == 3
        
        # Verify all notifications are marked as read
        unread_count = await Notification.objects.filter(
            recipient=user,
            is_read=False
        ).acount()
        assert unread_count == 0
        
        # Close connection
        await communicator.disconnect()

    async def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong keep-alive."""
        # Create test user
        user = await User.objects.acreate(
            username='testuser5',
            email='test5@example.com'
        )
        
        # Connect to WebSocket
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Receive connection confirmation
        await communicator.receive_json_from()
        
        # Send ping
        timestamp = 1234567890
        await communicator.send_json_to({
            'type': 'ping',
            'timestamp': timestamp
        })
        
        # Receive pong
        response = await communicator.receive_json_from()
        assert response['type'] == 'pong'
        assert response['timestamp'] == timestamp
        
        # Close connection
        await communicator.disconnect()

    async def test_websocket_error_handling(self):
        """Test WebSocket error handling with invalid JSON."""
        # Create test user
        user = await User.objects.acreate(
            username='testuser6',
            email='test6@example.com'
        )
        
        # Connect to WebSocket
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user
        
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Receive connection confirmation
        await communicator.receive_json_from()
        
        # Send invalid message (will be caught by exception handler)
        await communicator.send_to(text_data="invalid json {")
        
        # Should receive error response
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        assert 'Invalid JSON' in response['message']
        
        # Close connection
        await communicator.disconnect()


@pytest.mark.django_db
class TestNotificationServiceBroadcasting:
    """Test NotificationService WebSocket broadcasting."""

    def test_notification_service_broadcasts(self):
        """Test that NotificationService broadcasts notifications."""
        # Create test user
        user = User.objects.create_user(
            username='testuser7',
            email='test7@example.com',
            password='testpass123'
        )
        
        # Send notification using NotificationService
        notification = NotificationService.send_notification(
            recipient=user,
            title='Service Test',
            message='Testing NotificationService broadcasting',
            category='info'
        )
        
        # Verify notification was created
        assert notification.id is not None
        assert notification.title == 'Service Test'
        assert notification.recipient == user
        
        # Note: WebSocket broadcasting is tested separately above
        # This test verifies the service layer integration

    def test_bulk_notification_broadcasting(self):
        """Test bulk notification broadcasting."""
        # Create multiple test users
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'bulkuser{i}',
                email=f'bulk{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        # Send bulk notifications
        notifications = NotificationService.send_bulk_notifications(
            recipients=users,
            title='Bulk Test',
            message='Testing bulk notifications'
        )
        
        # Verify notifications were created
        assert len(notifications) == 3
        for notification in notifications:
            assert notification.title == 'Bulk Test'
            assert notification.is_read is False

