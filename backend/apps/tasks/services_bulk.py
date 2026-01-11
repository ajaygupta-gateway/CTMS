from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.tasks.models import Task, TaskHistory
from apps.tasks.services import complete_parent_task, block_child_task


def bulk_update_tasks(task_ids, new_status, user):
    tasks = list(
        Task.objects
        .select_related("parent_task")
        .prefetch_related("child_tasks")
        .filter(id__in=task_ids)
    )

    if len(tasks) != len(task_ids):
        raise ValidationError("One or more task IDs are invalid.")

    # 🔐 PERMISSION VALIDATION (MISSING PART)
    for task in tasks:
        # Auditors never allowed
        if user.is_auditor():
            raise ValidationError("Auditors cannot update tasks.")

        # Developers can update ONLY their own tasks
        if user.is_developer() and task.assigned_to_id != user.id:
            raise ValidationError(
                f"You do not have permission to update task '{task.title}'."
            )

    task_map = {task.id: task for task in tasks}

    # ---------- GLOBAL VALIDATION ----------
    for task in tasks:
        if new_status == "completed" and task.is_parent():
            for child in task.child_tasks.all():
                if child.status in ("in_progress", "blocked"):
                    raise ValidationError(
                        f"Cannot complete parent task '{task.title}'. "
                        f"Child '{child.title}' is {child.status}."
                    )

        if new_status == "blocked" and task.parent_task:
            parent = task.parent_task
            if parent.id not in task_map and parent.status == "completed":
                raise ValidationError(
                    f"Cannot block child '{task.title}' because parent "
                    f"'{parent.title}' is already completed."
                )

    # ---------- ATOMIC UPDATE ----------
    with transaction.atomic():
        for task in tasks:
            old_status = task.status
            task.status = new_status
            task.save(update_fields=["status"])

            TaskHistory.objects.create(
                task=task,
                action="Bulk status update",
                from_status=old_status,
                to_status=new_status,
            )

            if new_status == "completed" and task.is_parent():
                complete_parent_task(task)

            if new_status == "blocked" and task.parent_task:
                block_child_task(task)

