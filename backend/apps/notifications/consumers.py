import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Features:
    - JWT authentication via query params
    - User-specific notification channels
    - Automatic delivery status tracking
    - Support for offline message queuing
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Authenticate user via JWT token and add to their notification group.
        """
        # Get token from query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        
        if not token:
            await self.close(code=4001)  # Unauthorized
            return
        
        # Authenticate user
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await self.get_user(user_id)
            
            if not self.user:
                await self.close(code=4001)
                return
                
        except (TokenError, KeyError):
            await self.close(code=4001)
            return
        
        # Add to user-specific notification group
        self.room_group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send any pending undelivered notifications
        await self.send_pending_notifications()
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Remove from notification group.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Currently supports marking notifications as read.
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'read_confirmation',
                        'notification_id': notification_id
                    }))
            
            elif action == 'mark_all_read':
                await self.mark_all_notifications_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_read_confirmation'
                }))
                
        except json.JSONDecodeError:
            pass
    
    async def notification_message(self, event):
        """
        Handle notification message from channel layer.
        Send notification to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
        
        # Mark as delivered
        notification_id = event['notification'].get('id')
        if notification_id:
            await self.mark_notification_delivered(notification_id)
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def send_pending_notifications(self):
        """Send any undelivered notifications to the user."""
        notifications = Notification.objects.filter(
            user=self.user,
            is_delivered=False
        ).order_by('created_at')[:50]  # Limit to 50 most recent
        
        for notification in notifications:
            # Send via async method
            import asyncio
            asyncio.create_task(self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': {
                    'id': notification.id,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'task_id': notification.task_id,
                    'created_at': notification.created_at.isoformat(),
                    'read': notification.read,
                }
            })))
            
            # Mark as delivered
            notification.is_delivered = True
            notification.save()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user."""
        Notification.objects.filter(
            user=self.user,
            read=False
        ).update(read=True)
    
    @database_sync_to_async
    def mark_notification_delivered(self, notification_id):
        """Mark a notification as delivered."""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_delivered = True
            notification.save()
        except Notification.DoesNotExist:
            pass
