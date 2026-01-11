from django.contrib import admin
from .models import APIAuditLog


@admin.register(APIAuditLog)
class APIAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "method",
        "endpoint",
        "status_code",
    )
    list_filter = ("method", "status_code")
    search_fields = ("endpoint", "user__username")
    readonly_fields = (
        "user",
        "endpoint",
        "method",
        "status_code",
        "request_body",
        "response_body",
        "timestamp",
    )
