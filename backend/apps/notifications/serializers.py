from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_status = serializers.CharField(source='task.status', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'message',
            'notification_type',
            'task',
            'task_title',
            'task_status',
            'created_at',
            'read',
            'is_delivered'
        ]
        read_only_fields = ['id', 'created_at', 'is_delivered']
