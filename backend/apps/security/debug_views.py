import time
from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.security.middleware.smart_rate_limit import (
    RATE_LIMITS,
    WINDOW_SECONDS,
)


class DebugRateLimitViewSet(viewsets.ModelViewSet):
    """
    DEBUG ONLY:
    Shows current rate-limit usage for the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    queryset = []  # IMPORTANT: no model backing this view
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        if not settings.DEBUG:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        role = user.role

        current_window = int(time.time() // WINDOW_SECONDS)

        data = {
            "user_id": user.id,
            "role": role,
            "window_seconds": WINDOW_SECONDS,
            "limits": RATE_LIMITS.get(role),
            "current_usage": {},
        }

        for action in ("read", "write"):
            key = f"rate:{user.id}:{role}:{action}:{current_window}"
            data["current_usage"][action] = cache.get(key, 0)

        return Response(data, status=status.HTTP_200_OK)
