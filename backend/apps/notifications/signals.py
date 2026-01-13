from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.tasks.models import Task
from .models import Notification


@receiver(pre_save, sender=Task)
def track_state_change(sender, instance, **kwargs):
    """
    Track previous status and assignee before saving to detect changes.
    """
    if instance.pk:
        try:
            previous = Task.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
            instance._previous_assigned_to = previous.assigned_to
        except Task.DoesNotExist:
            instance._previous_status = None
            instance._previous_assigned_to = None
    else:
        instance._previous_status = None
        instance._previous_assigned_to = None


@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    """
    Send notification when:
    1. Task is created (assigned user)
    2. Task status changes (assigned user)
    3. Task is reassigned (new assigned user)
    """
    notified_users = set()

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
    
    # Check if assignee changed
    previous_assigned_to = getattr(instance, '_previous_assigned_to', None)
    if previous_assigned_to and previous_assigned_to != instance.assigned_to:
        # 1. Notify the PREVIOUS user (Unassigned)
        notification_unassigned = Notification.objects.create(
            user=previous_assigned_to,
            task=instance,
            message=f"You have been unassigned from task: {instance.title}",
            notification_type='task_unassigned'
        )
        send_notification_to_user(previous_assigned_to.id, notification_unassigned)
        notified_users.add(previous_assigned_to.id)

        # 2. Notify the NEW user (Assigned) - if there is one (not None)
        if instance.assigned_to:
            notification_assigned = Notification.objects.create(
                user=instance.assigned_to,
                task=instance,
                message=f"You have been assigned a task: {instance.title}",
                notification_type='task_assigned'
            )
            send_notification_to_user(instance.assigned_to.id, notification_assigned)
            notified_users.add(instance.assigned_to.id)
    
    # Check if status changed
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status and previous_status != instance.status:
        # Status changed - notify the assigned user
        # Only notify if we haven't already sent an assignment notification to this user
        if instance.assigned_to and instance.assigned_to.id not in notified_users:
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
        # Note: We do NOT mark as delivered here. 
        # The Consumer will mark it as delivered upon actual sending.
    except Exception as e:
        # If sending fails, it remains in DB with is_delivered=False
        print(f"Failed to send notification to user {user_id}: {e}")
