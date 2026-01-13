from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.tasks.models import Task
from .models import Notification
from .signals import send_notification_to_user


@shared_task
def check_deadline_warnings():
    """
    Celery task to check for tasks approaching deadline.
    Sends notification 1 hour before deadline.
    
    This should be scheduled to run every 5-10 minutes via Celery Beat.
    """
    now = timezone.now()
    one_hour_later = now + timedelta(hours=1)
    
    # Find tasks with deadline within the next hour that are not completed
    upcoming_tasks = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=one_hour_later,
        status__in=['pending', 'in_progress', 'blocked']
    ).select_related('assigned_to')
    
    for task in upcoming_tasks:
        # Check if we already sent a warning for this task
        existing_notification = Notification.objects.filter(
            task=task,
            notification_type='deadline_warning',
            created_at__gte=now - timedelta(hours=2)  # Don't spam if already sent recently
        ).exists()
        
        if not existing_notification:
            # Calculate time remaining
            time_remaining = task.deadline - now
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            
            # Create notification
            notification = Notification.objects.create(
                user=task.assigned_to,
                task=task,
                message=f"⚠️ Task '{task.title}' deadline approaching in {minutes_remaining} minutes!",
                notification_type='deadline_warning'
            )
            
            # Send via WebSocket
            send_notification_to_user(task.assigned_to.id, notification)
    
    return f"Checked {upcoming_tasks.count()} tasks approaching deadline"


@shared_task
def cleanup_old_notifications():
    """
    Celery task to clean up old read notifications.
    Keeps unread notifications and recent read notifications (last 30 days).
    
    This should be scheduled to run daily via Celery Beat.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    deleted_count, _ = Notification.objects.filter(
        read=True,
        created_at__lt=thirty_days_ago
    ).delete()
    
    return f"Deleted {deleted_count} old notifications"
