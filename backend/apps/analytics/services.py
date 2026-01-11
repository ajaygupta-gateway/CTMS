from django.db.models import Count, Avg, F
from django.utils.timezone import now

from apps.tasks.models import Task


def calculate_my_tasks(user):
    qs = Task.objects.filter(assigned_to=user)

    total = qs.count()

    by_status = {
        row["status"]: row["count"]
        for row in qs.values("status").annotate(count=Count("id"))
    }

    overdue_count = qs.filter(
        deadline__lt=now(),
        status__in=["pending", "in_progress", "blocked"],
    ).count()

    avg_hours = qs.filter(
        status="completed",
        actual_hours__isnull=False,
    ).aggregate(avg=Avg("actual_hours"))["avg"]

    return {
        "total": total,
        "by_status": by_status,
        "overdue_count": overdue_count,
        "avg_completion_time": (
            f"{round(float(avg_hours), 2)} hours" if avg_hours else None
        ),
    }


def calculate_team_tasks(user):
    qs = Task.objects.all() if user.is_manager() else Task.objects.filter(assigned_to=user)

    priority_distribution = {
        row["priority"]: row["count"]
        for row in qs.values("priority").annotate(count=Count("id"))
    }

    blocked = qs.filter(status="blocked").values(
        "id", "title", "assigned_to"
    )

    return {
        "total": qs.count(),
        "blocked_tasks_needing_attention": list(blocked),
        "priority_distribution": priority_distribution,
    }


def calculate_efficiency_score(user):
    qs = Task.objects.filter(
        assigned_to=user,
        status="completed",
        actual_hours__isnull=False,
        estimated_hours__isnull=False,
    )

    total = qs.count()
    if total == 0:
        return 0.0

    on_time = qs.filter(actual_hours__lte=F("estimated_hours")).count()
    on_time_ratio = on_time / total

    avg_ratio = qs.aggregate(
        ratio=Avg(F("actual_hours") / F("estimated_hours"))
    )["ratio"]

    bonus = 1.2 if avg_ratio and avg_ratio <= 1 else 0.8

    return round(on_time_ratio * bonus * 100, 2)
