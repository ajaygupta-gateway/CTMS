from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from apps.tasks.models import Task
from apps.notifications.models import Notification

PRIORITY_ORDER = ["low", "medium", "high", "critical"]


class PriorityEscalationMiddleware:
    """
    Escalates task priority automatically when deadline is within 24 hours.
    Runs on every API request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only escalate AFTER successful request
        if response.status_code >= 400:
            return response

        now = timezone.now()
        threshold = now + timedelta(hours=24)

        # Fetch only eligible tasks
        tasks = Task.objects.filter(
            status__in=["pending", "in_progress", "blocked"],
            deadline__lte=threshold,
            priority_escalated=False,
        ).select_related("assigned_to")

        for task in tasks:
            self._escalate_task(task)

        return response

    def _escalate_task(self, task: Task):
        try:
            current_index = PRIORITY_ORDER.index(task.priority)
        except ValueError:
            return

        if current_index >= len(PRIORITY_ORDER) - 1:
            return  # Already critical

        with transaction.atomic():
            new_priority = PRIORITY_ORDER[current_index + 1]

            task.priority = new_priority
            task.priority_escalated = True
            task.save(update_fields=["priority", "priority_escalated"])

            Notification.objects.create(
                user=task.assigned_to,
                task=task,
                message=f"Task '{task.title}' priority escalated to {new_priority.upper()} due to upcoming deadline.",
            )
