from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import (
    AuthRegisterViewSet,
    AuthVerifyEmailViewSet,
    AuthLoginViewSet,
    AuthRefreshViewSet,
    AuthLogoutViewSet,
    AuthLogoutAllViewSet,
    UserViewSet,
)
from .views_me import MeView

router = SimpleRouter()
router.register("register", AuthRegisterViewSet, basename="auth-register")
router.register("verify-email", AuthVerifyEmailViewSet, basename="auth-verify-email")
router.register("login", AuthLoginViewSet, basename="auth-login")
router.register("refresh", AuthRefreshViewSet, basename="auth-refresh")
router.register("logout", AuthLogoutViewSet, basename="auth-logout")
router.register("logout-all", AuthLogoutAllViewSet, basename="auth-logout-all")

# User directory (list / retrieve)
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    # Self profile (separate from user listing)
    path("users/me/", MeView.as_view(), name="users-me"),
]

urlpatterns += router.urls