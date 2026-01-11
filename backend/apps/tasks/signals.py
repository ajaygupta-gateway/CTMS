from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Task, TaskHistory

@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    if not instance.pk:
        return  # New task, ignore

    old = Task.objects.get(pk=instance.pk)

    if old.status != instance.status:
        TaskHistory.objects.create(
            task=instance,
            old_status=old.status,
            new_status=instance.status,
            changed_by=getattr(instance, "_changed_by", None),
        )
