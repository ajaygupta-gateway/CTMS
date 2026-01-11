from rest_framework.routers import SimpleRouter
from .views import TaskAnalyticsViewSet

router = SimpleRouter()
router.register("tasks/analytics", TaskAnalyticsViewSet, basename="task-analytics")

urlpatterns = router.urls
