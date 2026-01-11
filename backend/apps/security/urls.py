from rest_framework.routers import SimpleRouter
from .debug_views import DebugRateLimitViewSet

router = SimpleRouter()
router.register("rate-limit", DebugRateLimitViewSet, basename="debug-rate-limit")

urlpatterns = router.urls
