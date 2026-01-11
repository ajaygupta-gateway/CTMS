from rest_framework.viewsets import ModelViewSet
from .models import Task
from .serializers import TaskSerializer
from .permissions import TaskAccessPermission, TaskCreatePermission
from apps.users.permissions import AuditorReadOnly


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [
        AuditorReadOnly,
        TaskCreatePermission,
        TaskAccessPermission,
    ]

    def get_queryset(self):
        user = self.request.user

        qs = Task.objects.select_related(
            "assigned_to",
            "created_by",
            "parent_task",
        ).prefetch_related("child_tasks", "tags")

        # Auditors see everything (read-only)
        if user.is_auditor():
            return qs

        # Managers see everything
        if user.is_manager():
            return qs

        # Developers see:
        # 1) Tasks assigned to them
        # 2) Parent tasks they created (optional, but realistic)
        return qs.filter(
            assigned_to=user
        )

    def perform_create(self, serializer):
        """
        Force created_by to be request.user
        Prevent spoofing
        """
        serializer.save(created_by=self.request.user)
