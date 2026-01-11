from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Task, TaskHistory

"""
When parent marked completed:

Child pending → auto completed

Child in_progress / blocked →  ERROR

Log all cascades


cascade meaning:
Cascade means: one action automatically triggers other actions.
    
    here:
    
cascade = a status change in one task automatically changes other tasks.

"""
def complete_parent_task(parent_task: Task):
    children = parent_task.child_tasks.all()

    # Validate first (NO partial updates)
    for child in children:
        if child.status in ("in_progress", "blocked"):
            raise ValidationError(
                f"Cannot complete parent task. Child task '{child.title}' is {child.status}."
            )



    #transaction.atomic() = Guarantees: Either everything succeeds Or nothing changes

    # now handles if all child task are not in progress or blocked

    with transaction.atomic():
        old_status = parent_task.status
        parent_task.status = "completed"
        parent_task.save()

        TaskHistory.objects.create(
            task=parent_task,
            action="Parent task completed",
            from_status=old_status,
            to_status="completed",
        )

        for child in children:
            if child.status == "pending":
                TaskHistory.objects.create(
                    task=child,
                    action="Auto-completed due to parent completion",
                    from_status="pending",
                    to_status="completed",
                )
                child.status = "completed"
                child.save()

"""
Requirement Recap

If ANY child becomes blocked

Parent auto → blocked
"""
def block_child_task(child_task: Task):
    if not child_task.parent_task:
        return

    parent = child_task.parent_task

    if parent.status != "blocked":
        with transaction.atomic():
            old_status = parent.status
            parent.status = "blocked"
            parent.save()

            TaskHistory.objects.create(
                task=parent,
                action="Auto-blocked due to child task",
                from_status=old_status,
                to_status="blocked",
            )
