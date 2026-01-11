from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.tasks.serializers_bulk import BulkTaskUpdateSerializer
from apps.tasks.services_bulk import bulk_update_tasks
from apps.tasks.models import Task


class BulkTaskUpdateViewSet(viewsets.ModelViewSet):
    """
    POST /api/tasks/bulk-update/

    Performs atomic bulk status update with parent–child validation.
    This is an action-style endpoint, not real CRUD.
    """

    serializer_class = BulkTaskUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.none()   # IMPORTANT
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_ids = serializer.validated_data["task_ids"]
        new_status = serializer.validated_data["status"]

        bulk_update_tasks(
            task_ids=task_ids,
            new_status=new_status,
            user=request.user,
        )

        return Response(
            {
                "detail": f"{len(task_ids)} tasks updated successfully."
            },
            status=status.HTTP_200_OK,
        )
