import time

from django.core.cache import cache
from django.http import JsonResponse

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


READ_METHODS = ("GET", "HEAD", "OPTIONS")
WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")

RATE_LIMITS = {
    "developer": {"read": 100, "write": 20},
    "manager": {"read": 200, "write": 50},
    "auditor": {"read": None, "write": 0},  # unlimited read, no write
}

WINDOW_SECONDS = 60 * 60  # 1 hour


def get_window_key(user_id, role, action):
    """
    Generates a rolling window key per user, role, and action.
    """
    window = int(time.time() // WINDOW_SECONDS)
    return f"rate:{user_id}:{role}:{action}:{window}"


def increment_counter(key):
    """
    Increment request counter with TTL.
    """
    if cache.get(key) is None:
        cache.set(key, 1, WINDOW_SECONDS)
    else:
        cache.incr(key)


def get_counter(key):
    return cache.get(key, 0)


class SmartRateLimitMiddleware:
    """
    Role-aware, method-aware rate limiting middleware.

    Rules:
    - Developers: 100 READ / 20 WRITE per hour
    - Managers: 200 READ / 50 WRITE per hour
    - Auditors: Unlimited READ, 0 WRITE
    - ONLY successful responses (<400) are counted
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        """
        IMPORTANT:
        JWT authentication does NOT populate request.user at middleware level.
        We must authenticate manually here.
        """

        try:
            auth_result = self.jwt_auth.authenticate(request)
        except AuthenticationFailed:
            return self.get_response(request)

        if auth_result is None:
            return self.get_response(request)

        user, token = auth_result
        request.user = user  # make user available downstream

        method = request.method

        # Determine action type
        if method in READ_METHODS:
            action = "read"
        elif method in WRITE_METHODS:
            action = "write"
        else:
            return self.get_response(request)

        role = user.role
        limits = RATE_LIMITS.get(role)

        # Auditors can NEVER write
        if role == "auditor" and action == "write":
            return JsonResponse(
                {"detail": "Auditors are not allowed to modify data."},
                status=403,
            )

        # Unlimited READ (Auditors) → bypass rate limiting
        if limits[action] is None:
            return self.get_response(request)

        key = get_window_key(user.id, role, action)
        current_count = get_counter(key)

        # Rate limit exceeded
        if current_count >= limits[action]:
            response = JsonResponse(
                {"detail": f"{action.capitalize()} rate limit exceeded."},
                status=429,
            )

            # Required by spec
            if action == "write":
                response["X-Write-Available-In"] = cache.ttl(key) or WINDOW_SECONDS

            return response

        # Allow request to proceed
        response = self.get_response(request)

        # Count ONLY successful responses
        if response.status_code < 400:
            increment_counter(key)

        return response
