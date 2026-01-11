from rest_framework.routers import SimpleRouter

from .views import (TaskViewSet)
from .views_bulk import BulkTaskUpdateViewSet

router = SimpleRouter()

router.register("bulk-update", BulkTaskUpdateViewSet, basename="tasks-bulk-update")
router.register("", TaskViewSet, basename="task")

urlpatterns = router.urls

