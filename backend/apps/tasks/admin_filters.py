from django.contrib.admin import SimpleListFilter
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import F


class TasksNeedingAttentionFilter(SimpleListFilter):
    title = "Tasks Needing Attention"
    parameter_name = "needs_attention"

    def lookups(self, request, model_admin):
        return (
            ("blocked", "Blocked tasks"),
            ("overdue", "Overdue > 3 days"),
            ("overworked", "Actual hours > 1.5× estimated"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "blocked":
            return queryset.filter(status="blocked")

        if value == "overdue":
            overdue_date = now() - timedelta(days=3)
            return queryset.filter(
                deadline__lt=overdue_date,
                status__in=["pending", "in_progress", "blocked"],
            )

        if value == "overworked":
            return queryset.filter(
                actual_hours__isnull=False,
                estimated_hours__isnull=False,
                actual_hours__gt=F("estimated_hours") * 1.5,
            )

        return queryset
