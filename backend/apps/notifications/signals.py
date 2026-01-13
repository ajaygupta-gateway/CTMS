from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.tasks.models import Task
from .models import Notification


@receiver(pre_save, sender=Task)
def track_status_change(sender, instance, **kwargs):
    """
    Track the previous status before saving to detect changes.
    """
    if instance.pk:
        try:
            instance._previous_status = Task.objects.get(pk=instance.pk).status
        except Task.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Task)
def send_status_change_notification(sender, instance, created, **kwargs):
    """
    Send notification when a task's status changes.
    Only notify the assigned user if the status changed.
    """
    if created:
        # Task was just created - send assignment notification
        notification = Notification.objects.create(
            user=instance.assigned_to,
            task=instance,
            message=f"You have been assigned a new task: {instance.title}",
            notification_type='task_assigned'
        )
        send_notification_to_user(instance.assigned_to.id, notification)
        return
    
    # Check if status changed
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status and previous_status != instance.status:
        # Status changed - notify the assigned user
        status_display = dict(Task.STATUS_CHOICES).get(instance.status, instance.status)
        
        notification = Notification.objects.create(
            user=instance.assigned_to,
            task=instance,
            message=f"Task '{instance.title}' status changed to {status_display}",
            notification_type='status_change'
        )
        send_notification_to_user(instance.assigned_to.id, notification)


def send_notification_to_user(user_id, notification):
    """
    Send notification to user via WebSocket.
    If user is offline, notification will be queued in database.
    """
    channel_layer = get_channel_layer()
    
    # Prepare notification data
    notification_data = {
        'id': notification.id,
        'message': notification.message,
        'notification_type': notification.notification_type,
        'task_id': notification.task_id,
        'created_at': notification.created_at.isoformat(),
        'read': notification.read,
    }
    
    # Send to user's notification group
    try:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        # If successfully sent, mark as delivered
        notification.is_delivered = True
        notification.save()
    except Exception as e:
        # If sending fails (user offline), notification remains in DB
        # with is_delivered=False and will be sent when user connects
        print(f"Failed to send notification to user {user_id}: {e}")
