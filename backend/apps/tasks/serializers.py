from rest_framework import serializers
from .models import Task
from .services import complete_parent_task, block_child_task
from apps.users.models import User


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    assigned_to_user = serializers.CharField(
        source="assigned_to.username",
        read_only=True
    )
    created_by_user = serializers.CharField(
        source="created_by.username",
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "estimated_hours",
            "actual_hours",
            "deadline",
            "priority_escalated",
            "created_at",
            "updated_at",
            "assigned_to",
            "assigned_to_user",
            "created_by",
            "created_by_user",
            "parent_task",
            "tags",
        ]
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)  #e.g {"status": "completed"}


        # Parent → completed
        if new_status == "completed" and instance.is_parent(): #If this is a parent: Delegate to service
            complete_parent_task(instance)
            return instance

        # Child → blocked
        if new_status == "blocked" and instance.parent_task:  #If this is a child: Save child, Then update parent
            instance.status = "blocked"
            instance.save()
            block_child_task(instance)
            return instance

        return super().update(instance, validated_data)
