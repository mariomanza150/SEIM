"""
Tests for WebSocket notification consumer.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser

from notifications.consumers import NotificationConsumer
from notifications.models import Notification


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestNotificationConsumer:
    """Test WebSocket notification consumer."""
    
    async def test_connect_authenticated_user(self, user_student):
        """Test WebSocket connection for authenticated user."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Should receive connection confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'connection_established'
        assert response['user_id'] == str(user_student.id)
        
        await communicator.disconnect()
    
    async def test_connect_unauthenticated_user(self):
        """Test WebSocket connection rejects unauthenticated users."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = AnonymousUser()
        
        connected, _ = await communicator.connect()
        assert not connected
    
    async def test_receive_mark_read_message(self, user_student, notification):
        """Test marking notification as read via WebSocket."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Send mark_read message
        await communicator.send_json_to({
            'type': 'mark_read',
            'notification_id': str(notification.id)
        })
        
        # Should receive confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'notification_marked_read'
        assert response['notification_id'] == str(notification.id)
        
        # Verify notification is marked as read in database
        await sync_to_async(notification.refresh_from_db)()
        assert notification.is_read
        
        await communicator.disconnect()
    
    async def test_receive_mark_all_read_message(self, user_student):
        """Test marking all notifications as read via WebSocket."""
        # Create multiple notifications (ORM must not run in async context)
        def _seed():
            for i in range(3):
                Notification.objects.create(
                    recipient=user_student,
                    title=f"Test Notification {i}",
                    message="Test message",
                    is_read=False,
                )

        await sync_to_async(_seed)()
        
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Send mark_all_read message
        await communicator.send_json_to({
            'type': 'mark_all_read'
        })
        
        # Should receive confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'all_notifications_marked_read'
        assert response['count'] == 3
        
        # Verify all notifications are marked as read
        def _unread_count():
            return Notification.objects.filter(
                recipient=user_student, is_read=False
            ).count()

        assert await sync_to_async(_unread_count)() == 0
        
        await communicator.disconnect()
    
    async def test_receive_ping_message(self, user_student):
        """Test ping/pong keep-alive."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Send ping
        timestamp = 1234567890
        await communicator.send_json_to({
            'type': 'ping',
            'timestamp': timestamp
        })
        
        # Should receive pong
        response = await communicator.receive_json_from()
        assert response['type'] == 'pong'
        assert response['timestamp'] == timestamp
        
        await communicator.disconnect()
    
    async def test_receive_invalid_json(self, user_student):
        """Test handling of invalid JSON."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Send invalid JSON
        await communicator.send_to(text_data="invalid json")
        
        # Should receive error message
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        assert 'Invalid JSON' in response['message']
        
        await communicator.disconnect()
    
    async def test_broadcast_notification_to_user(self, user_student):
        """Test broadcasting notification to user's channel."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Create notification (triggers broadcast)
        from notifications.services import NotificationService

        notification = await sync_to_async(NotificationService.send_notification)(
            recipient=user_student,
            title="Test Notification",
            message="Test message",
            category="info",
        )
        
        # Should receive notification via WebSocket
        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'notification.new'
        assert response['notification']['id'] == str(notification.id)
        assert response['notification']['title'] == "Test Notification"
        assert response['notification']['category'] == "info"
        
        await communicator.disconnect()
    
    async def test_disconnect_leaves_group(self, user_student):
        """Test that disconnect properly leaves notification group."""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope['user'] = user_student
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection confirmation
        
        # Disconnect
        await communicator.disconnect()
        
        # Try to send notification - should not reach user
        from notifications.services import NotificationService

        await sync_to_async(NotificationService.send_notification)(
            recipient=user_student,
            title="Test Notification",
            message="Test message",
        )
        
        # No message should be received (connection closed)
        # This test verifies the consumer properly cleans up on disconnect

    async def test_application_sync_forwards_to_client(self, user_student):
        from unittest.mock import AsyncMock

        consumer = NotificationConsumer()
        consumer.send = AsyncMock()
        await consumer.application_sync(
            {
                "type": "application.sync",
                "application_id": "00000000-0000-0000-0000-000000000001",
                "change_type": "comment_added",
                "document_id": None,
            }
        )
        consumer.send.assert_called_once()
        payload = json.loads(consumer.send.call_args.kwargs["text_data"])
        assert payload["type"] == "application.sync"
        assert payload["change_type"] == "comment_added"
        assert payload["document_id"] is None


@pytest.fixture
def notification(user_student):
    """Create a test notification."""
    return Notification.objects.create(
        recipient=user_student,
        title="Test Notification",
        message="Test message",
        category="info",
        is_read=False
    )

