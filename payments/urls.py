from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet
from .webhook import stripe_webhook

router = DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("webhook/stripe/", stripe_webhook),
]

urlpatterns += router.urls