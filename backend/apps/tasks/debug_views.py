from datetime import timedelta
from django.conf import settings
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task


class DebugPriorityEscalationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not settings.DEBUG:
            return Response({"detail": "Not found."}, status=404)

        cutoff = now() + timedelta(hours=24)

        tasks = Task.objects.filter(
            deadline__lte=cutoff,
            priority_escalated=False,
        ).exclude(status="completed")

        result = []

        priority_order = ["low", "medium", "high", "critical"]

        for task in tasks:
            current_index = priority_order.index(task.priority)
            next_priority = (
                priority_order[current_index + 1]
                if current_index < len(priority_order) - 1
                else "critical"
            )

            result.append({
                "task_id": task.id,
                "title": task.title,
                "current_priority": task.priority,
                "will_escalate_to": next_priority,
                "deadline_in_hours": round(
                    (task.deadline - now()).total_seconds() / 3600,
                    2,
                ),
            })

        return Response({
            "count": len(result),
            "tasks": result,
        })
