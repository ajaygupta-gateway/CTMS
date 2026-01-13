from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notifications.
    
    Endpoints:
    - GET /api/notifications/ - List user's notifications
    - GET /api/notifications/{id}/ - Get specific notification
    - POST /api/notifications/{id}/mark_read/ - Mark notification as read
    - POST /api/notifications/mark_all_read/ - Mark all notifications as read
    - GET /api/notifications/unread_count/ - Get count of unread notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's notifications."""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all user's notifications as read."""
        updated = Notification.objects.filter(
            user=request.user,
            read=False
        ).update(read=True)
        return Response({'status': f'{updated} notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            user=request.user,
            read=False
        ).count()
        return Response({'count': count})


# Create your views here.
