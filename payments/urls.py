from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, create_payment_intent
from .webhook import stripe_webhook

router = DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("create-intent/", create_payment_intent),
    path("webhook/stripe/", stripe_webhook),
]

urlpatterns += router.urls