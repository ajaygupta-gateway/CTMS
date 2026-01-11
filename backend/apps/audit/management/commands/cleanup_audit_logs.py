from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from apps.audit.models import APIAuditLog


class Command(BaseCommand):
    help = "Delete audit2 logs older than 30 days"

    def handle(self, *args, **options):
        cutoff = now() - timedelta(days=30)
        deleted, _ = APIAuditLog.objects.filter(
            timestamp__lt=cutoff
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} old audit2 logs.")
        )
