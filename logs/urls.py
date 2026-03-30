from rest_framework.routers import DefaultRouter
from .views import LogViewSet

router = DefaultRouter()
router.register("", LogViewSet)

urlpatterns = router.urls