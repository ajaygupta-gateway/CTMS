from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


FAILED_WINDOW = 10 * 60        # 10 minutes
BLOCK_DURATION = 60 * 60       # 1 hour
MAX_FAILURES = 5


class IPSecurityMiddleware:
    """
    Handles (API ONLY):
    - Smart CORS
    - Failed login tracking
    - Temporary IP blocking
    - CAPTCHA challenge

    Explicitly bypasses Django Admin and non-API routes.
    """

    API_PREFIX = "/api/"
    ADMIN_PREFIX = "/admin/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # -------------------------------------------------
        # 1️⃣ Bypass Django Admin completely
        # -------------------------------------------------
        if path.startswith(self.ADMIN_PREFIX):
            return self.get_response(request)

        # -------------------------------------------------
        # 2️⃣ Apply security ONLY to API routes
        # -------------------------------------------------
        if not path.startswith(self.API_PREFIX):
            return self.get_response(request)

        ip = self.get_client_ip(request)

        # -------------------------------------------------
        # 3️⃣ CORS CHECK (API only)
        # -------------------------------------------------
        origin = request.headers.get("Origin")
        if origin and origin not in settings.ALLOWED_ORIGINS:
            return JsonResponse(
                {"detail": "CORS origin not allowed"},
                status=403,
            )

        # -------------------------------------------------
        # 4️⃣ IP BLOCK CHECK
        # -------------------------------------------------
        block_key = f"ip-blocked:{ip}"
        captcha_key = f"captcha:{ip}"

        if cache.get(block_key):
            expected_answer = cache.get(captcha_key)
            provided_answer = request.headers.get("X-Captcha-Answer")

            if not provided_answer or provided_answer != expected_answer:
                return JsonResponse(
                    {
                        "detail": "IP blocked. Solve CAPTCHA.",
                        "captcha": cache.get(f"captcha-question:{ip}"),
                    },
                    status=403,
                )

            # CAPTCHA solved → unblock
            cache.delete(block_key)
            cache.delete(captcha_key)
            cache.delete(f"captcha-question:{ip}")

        # -------------------------------------------------
        # 5️⃣ Continue request
        # -------------------------------------------------
        response = self.get_response(request)

        # -------------------------------------------------
        # 6️⃣ FAILED AUTH TRACKING (API only)
        # -------------------------------------------------
        if response.status_code in (400, 401):
            self.track_failure(ip)

        return response

    # -----------------------------------------------------
    # Helper methods
    # -----------------------------------------------------

    def track_failure(self, ip):
        fail_key = f"fail:{ip}"
        count = cache.get(fail_key, 0) + 1
        cache.set(fail_key, count, FAILED_WINDOW)

        if count >= MAX_FAILURES:
            self.block_ip(ip)

    def block_ip(self, ip):
        captcha = self.create_captcha()
        cache.set(f"ip-blocked:{ip}", True, BLOCK_DURATION)
        cache.set(f"captcha:{ip}", captcha["answer"], BLOCK_DURATION)
        cache.set(
            f"captcha-question:{ip}",
            captcha["question"],
            BLOCK_DURATION,
        )

    def create_captcha(self):
        from apps.security.utils import generate_captcha
        return generate_captcha()

    def get_client_ip(self, request):
        return request.META.get("REMOTE_ADDR")
