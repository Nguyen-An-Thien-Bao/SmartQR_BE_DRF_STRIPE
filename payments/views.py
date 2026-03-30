import stripe
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(order__table__tenant_admin=user)

    def create(self, request, *args, **kwargs):
        order_id = request.data.get("order")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Multi-tenant check
        if order.table.tenant_admin != request.user:
            return Response({"error": "Not your order"}, status=403)

        amount = int(order.total_price * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "order_id": str(order.id),
                "user_id": str(request.user.id),
            }
        )

        payment = Payment.objects.create(
            order=order,
            amount=amount,
            stripe_payment_intent=intent.id
        )

        return Response({
            "client_secret": intent.client_secret,
            "payment_id": payment.id
        })