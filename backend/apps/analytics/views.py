from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import (
    calculate_my_tasks,
    calculate_team_tasks,
    calculate_efficiency_score,
)


class TaskAnalyticsViewSet(viewsets.ModelViewSet):
    """
    GET /api/tasks/analytics/

    Read-only analytics endpoint.
    Action-style ViewSet (not real CRUD).
    """

    permission_classes = [IsAuthenticated]
    queryset = []  # prevents accidental data exposure
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        user = request.user

        return Response({
            "my_tasks": calculate_my_tasks(user),
            "team_tasks": calculate_team_tasks(user),
            "efficiency_score": calculate_efficiency_score(user),
        })
