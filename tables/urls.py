from rest_framework.routers import DefaultRouter
from .views import TableViewSet

router = DefaultRouter()
router.register("", TableViewSet)

urlpatterns = router.urls