"""
WebSocket consumer for real-time notifications.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    
    Features:
    - User authentication (JWT or session)
    - Subscribe to personal notification channel
    - Real-time notification delivery
    - Mark notifications as read via WebSocket
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Authenticate user and subscribe to their notification channel.
        """
        from django.contrib.auth.models import AnonymousUser
        
        self.user = self.scope.get("user")
        
        # Reject unauthenticated connections
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Create personal notification channel for this user
        self.notification_group_name = f"notifications_{self.user.id}"
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connection established',
            'user_id': str(self.user.id)
        }))
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Unsubscribe from notification channel.
        """
        if hasattr(self, 'notification_group_name'):
            # Leave notification group
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages from client.
        
        Supported message types:
        - mark_read: Mark notification(s) as read
        - ping: Keep-alive ping
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'notification_marked_read',
                        'notification_id': notification_id
                    }))
            
            elif message_type == 'mark_all_read':
                count = await self.mark_all_notifications_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_notifications_marked_read',
                    'count': count
                }))
            
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def notification_new(self, event):
        """
        Handle new notification event.
        Send notification to WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification.new',
            'notification': event['notification']
        }))
    
    async def notification_read(self, event):
        """
        Handle notification read event.
        Notify client that notification was marked as read.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification.read',
            'notification_id': event['notification_id']
        }))
    
    async def notification_update(self, event):
        """
        Handle notification update event.
        Send updated notification to client.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification.update',
            'notification': event['notification']
        }))

    async def application_sync(self, event):
        """Notify SPA to refetch application / document detail (no DB notification row)."""
        await self.send(text_data=json.dumps({
            'type': 'application.sync',
            'application_id': event['application_id'],
            'change_type': event['change_type'],
            'document_id': event.get('document_id'),
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read in the database.
        """
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """
        Mark all notifications as read for the current user.
        """
        from .models import Notification
        count = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True)
        return count

