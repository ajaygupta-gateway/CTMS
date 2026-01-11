from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from zoneinfo import available_timezones


class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        DEVELOPER = "developer", "Developer"
        AUDITOR = "auditor", "Auditor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER,
    )

    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in sorted(available_timezones())],
        default="Asia/Kolkata",
    )

    email_verified = models.BooleanField(default=False)

    def is_manager(self):
        return self.role == self.Role.MANAGER

    def is_developer(self):
        return self.role == self.Role.DEVELOPER

    def is_auditor(self):
        return self.role == self.Role.AUDITOR


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.TextField()
    device_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_used"]


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification token for {self.user.username}"
