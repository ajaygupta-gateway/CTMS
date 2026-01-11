from rest_framework import serializers

class BulkTaskUpdateSerializer(serializers.Serializer):
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
    )
    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "blocked", "completed"]
    )
