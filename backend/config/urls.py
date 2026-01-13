from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API endpoints
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.analytics.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/", include("apps.notifications.urls")),

    # Swagger/OpenAPI documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Debug-only endpoints
if settings.DEBUG:
    urlpatterns += [
        path("api/debug/", include("apps.security.urls")),
    ]
