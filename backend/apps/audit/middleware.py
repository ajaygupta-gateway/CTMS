import json

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from .models import APIAuditLog
from .utils import mask_sensitive_data


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Logs API requests & responses with masking and exclusions.
    """

    EXCLUDED_PATHS = (
        "/api/tasks/analytics/",
    )

    WRITE_METHODS = ("POST", "PUT", "PATCH")

    def process_request(self, request):
        request._audit_request_body = None

        if request.method in self.WRITE_METHODS:
            try:
                body = json.loads(request.body.decode())
                request._audit_request_body = mask_sensitive_data(body)
            except Exception:
                request._audit_request_body = None

    def process_response(self, request, response):
        path = request.path

        if path.startswith(self.EXCLUDED_PATHS):
            return response

        user = request.user if request.user.is_authenticated else None

        response_body = None
        if response.status_code >= 400:
            try:
                response_body = json.loads(response.content.decode())
            except Exception:
                response_body = None

        APIAuditLog.objects.create(
            user=user,
            endpoint=path,
            method=request.method,
            status_code=response.status_code,
            request_body=request._audit_request_body,
            response_body=response_body,
        )

        return response
