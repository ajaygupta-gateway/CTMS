import uuid

from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from .models import User, UserSession, EmailVerificationToken
from .serializers import UserSerializer
from .permissions import UserAccessPermission

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    RefreshSerializer, LogoutSerializer,
)


MAX_SESSIONS = 3



class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserAccessPermission]

    def get_queryset(self):
        user = self.request.user

        # Auditor → all users
        if user.is_auditor():
            return User.objects.all()

        # Manager → developers + self
        if user.is_manager():
            return User.objects.filter(
                role=User.Role.DEVELOPER
            ) | User.objects.filter(id=user.id)

        # Developer → self only
        return User.objects.filter(id=user.id)


class AuthRegisterViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token = EmailVerificationToken.objects.get(user=user)

        return Response(
            {
                "message": "User registered. Verify email to activate account.",
                "verification_token": str(token.token),
            },
            status=status.HTTP_201_CREATED,
        )




class AuthVerifyEmailViewSet(viewsets.ModelViewSet):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]
    queryset = EmailVerificationToken.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            verification = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            raise ValidationError("Invalid or expired verification token")

        user = verification.user
        user.email_verified = True
        user.save(update_fields=["email_verified"])

        verification.delete()

        return Response({"message": "Email verified successfully"})


class AuthLoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Enforce max sessions
        active_sessions = UserSession.objects.filter(user=user)
        if active_sessions.count() >= MAX_SESSIONS:
            devices = list(active_sessions.values_list("device_id", flat=True))
            raise ValidationError({
                "detail": "Maximum login limit reached.",
                "active_devices": devices,
            })

        user.last_login = now()
        user.save(update_fields=["last_login"])

        # Server-generated device ID
        device_id = request.COOKIES.get("device_id")
        if not device_id:
            device_id = str(uuid.uuid4())

        refresh = RefreshToken.for_user(user)

        UserSession.objects.create(
            user=user,
            refresh_token=str(refresh),
            device_id=device_id,
        )

        response = Response({
            "access": str(refresh.access_token),
        })

        # Store refresh token securely
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        # Store device id
        response.set_cookie(
            key="device_id",
            value=device_id,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response



class AuthRefreshViewSet(viewsets.ModelViewSet):
    serializer_class = RefreshSerializer  # can be empty serializer
    permission_classes = [AllowAny]
    queryset = UserSession.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            raise AuthenticationFailed("Refresh token missing")

        try:
            old_refresh = RefreshToken(refresh_token)
        except Exception:
            raise AuthenticationFailed("Invalid refresh token")

        old_refresh.blacklist()

        session = UserSession.objects.filter(refresh_token=refresh_token).first()
        if not session:
            raise AuthenticationFailed("Session not found")

        new_refresh = RefreshToken.for_user(session.user)

        session.refresh_token = str(new_refresh)
        session.save(update_fields=["refresh_token"])

        response = Response({
            "access": str(new_refresh.access_token),
        })

        response.set_cookie(
            key="refresh_token",
            value=str(new_refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response





class AuthLogoutViewSet(viewsets.ModelViewSet):
    serializer_class = LogoutSerializer  # can be empty
    permission_classes = [IsAuthenticated]
    queryset = UserSession.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

            UserSession.objects.filter(
                refresh_token=refresh_token,
                user=request.user
            ).delete()

        response = Response({"detail": "Logged out successfully"})
        response.delete_cookie("refresh_token")
        response.delete_cookie("device_id")

        return response



class AuthLogoutAllViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserSession.objects.none()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        sessions = UserSession.objects.filter(user=request.user)

        for session in sessions:
            try:
                RefreshToken(session.refresh_token).blacklist()
            except Exception:
                pass

        sessions.delete()

        response = Response({"detail": "Logged out from all devices"})
        response.delete_cookie("refresh_token")
        response.delete_cookie("device_id")

        return response
