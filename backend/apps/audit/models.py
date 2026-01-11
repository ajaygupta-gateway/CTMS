from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class APIAuditLog(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()

    request_body = models.JSONField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.endpoint} [{self.status_code}]"
