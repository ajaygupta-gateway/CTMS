import time
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

AUTO_REFRESH_THRESHOLD = 120  # seconds (2 minutes)


class JWTAutoRefreshMiddleware:
    """
    If an authenticated request is made in the last 2 minutes
    of access token validity, issue a new access token in response header.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = JWTAuthentication()

    def __call__(self, request):
        request._new_access_token = None

        header = self.auth.get_header(request)
        if header:
            raw_token = self.auth.get_raw_token(header)
            if raw_token:
                try:
                    validated_token = self.auth.get_validated_token(raw_token)

                    exp_timestamp = validated_token["exp"]
                    current_timestamp = int(time.time())
                    remaining_seconds = exp_timestamp - current_timestamp

                    if 0 < remaining_seconds <= AUTO_REFRESH_THRESHOLD:
                        user = self.auth.get_user(validated_token)
                        new_access = AccessToken.for_user(user)
                        request._new_access_token = str(new_access)

                except TokenError:
                    pass  # Let DRF handle invalid/expired token

        response = self.get_response(request)

        # Attach token ONLY for successful responses
        if (
            getattr(request, "_new_access_token", None)
            and response.status_code < 400
        ):
            response["X-New-Access-Token"] = request._new_access_token

        return response
