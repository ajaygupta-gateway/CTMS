from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    '''
    A Tag is just a label.

Examples:
    "backend"
    "urgent"
    "bug"
    "frontend"
    
    '''

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("completed", "Completed"),
    )

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    class Meta:
        indexes = [
            models.Index(fields=["deadline", "priority_escalated", "status"]),
        ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    assigned_to = models.ForeignKey(
        User, related_name="assigned_tasks", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, related_name="created_tasks", on_delete=models.CASCADE
    )

    parent_task = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="child_tasks",
        on_delete=models.CASCADE,
    )

    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2)
    actual_hours = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    deadline = models.DateTimeField()

    tags = models.ManyToManyField(Tag, blank=True)

    priority_escalated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_parent(self):
        return self.child_tasks.exists()

    def __str__(self):
        return self.title



class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_id}: {self.from_status} → {self.to_status}"
