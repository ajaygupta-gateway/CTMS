from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('status_change', 'Status Change'),
        ('deadline_warning', 'Deadline Warning'),
        ('task_assigned', 'Task Assigned'),
        ('task_unassigned', 'Task Unassigned'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='status_change')
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)  # Track if sent via WebSocket

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.message[:50]}"
