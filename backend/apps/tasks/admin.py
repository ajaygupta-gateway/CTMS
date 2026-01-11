from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from django.contrib.admin.helpers import ActionForm
from django import forms
import csv

from .models import Task
from .admin_filters import TasksNeedingAttentionFilter
from apps.users.models import User


class ReassignTaskActionForm(ActionForm):
    new_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Reassign to user",
        required=False,  # IMPORTANT: avoid crash on page load
    )


@admin.action(description="Generate Weekly Report (CSV)")
def generate_weekly_report(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="weekly_tasks_report.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "ID", "Title", "Status", "Priority",
        "Assigned To", "Created By",
        "Estimated Hours", "Actual Hours",
        "Deadline", "Created At",
    ])

    for task in queryset:
        writer.writerow([
            task.id,
            task.title,
            task.get_status_display(),
            task.get_priority_display(),
            task.assigned_to.username,
            task.created_by.username,
            task.estimated_hours,
            task.actual_hours,
            task.deadline,
            task.created_at,
        ])

    return response


@admin.action(description="Reassign Tasks to Another User")
def reassign_tasks(modeladmin, request, queryset):
    new_user = request.POST.get("new_user")

    if not new_user:
        messages.error(request, "Please select a user to reassign tasks.")
        return

    try:
        new_user = User.objects.get(pk=new_user)
    except User.DoesNotExist:
        messages.error(request, "Selected user does not exist.")
        return

    # CURRENT active tasks
    current_active = Task.objects.filter(
        assigned_to=new_user,
        status__in=["pending", "in_progress", "blocked"],
    ).count()

    # 🟢 INCOMING active tasks
    incoming_active = queryset.filter(
        status__in=["pending", "in_progress", "blocked"]
    ).count()

    # 🎯 PROJECTED load
    total_after_assignment = current_active + incoming_active

    if total_after_assignment > 10:
        messages.warning(
            request,
            f"Warning: {new_user.username} will have "
            f"{total_after_assignment} active tasks after reassignment."
        )

    updated = queryset.update(assigned_to=new_user)

    messages.success(
        request,
        f"{updated} tasks reassigned to {new_user.username}."
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    action_form = ReassignTaskActionForm

    actions = [
        generate_weekly_report,
        reassign_tasks,
    ]

    list_display = (
        "id",
        "title",
        "colored_status",
        "priority",
        "assigned_to",
        "deadline",
    )

    list_filter = (
        "status",
        "priority",
        TasksNeedingAttentionFilter,
    )

    search_fields = ("title", "description")

    def colored_status(self, obj):
        color_map = {
            "pending": "#6c757d",      # gray
            "in_progress": "#0d6efd",  # blue
            "blocked": "#dc3545",      # red
            "completed": "#198754",    # green
        }

        color = color_map.get(obj.status, "black")

        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            obj.get_status_display(),
        )

    colored_status.short_description = "Status"
