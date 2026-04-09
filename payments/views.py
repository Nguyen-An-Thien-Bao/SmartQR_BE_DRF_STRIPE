from django.utils import timezone
import stripe
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter
from orders.models import Order
from payments.services import PaymentService
from utils.get_price import get_price
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework.decorators import api_view, permission_classes

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_order_paid(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    user = request.user
    if user.role not in ["tenantAdmin", "waiter"]:
        return Response({"error": "Permission denied"}, status=403)

    method = request.data.get("method", "cash")
    order.payment_status = "paid"
    order.paid_at = timezone.now()
    order.save()

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": order.total_price,
            "status": "succeeded",
            "method": method
        }
    )

    if not created:
        payment.status = "succeeded"
        payment.amount = order.total_price
        payment.method = method
        payment.save()

    return Response({
        "message": "Order marked as paid (cash)"
    })

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["status", "amount"]

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
    

@api_view(['POST'])
@permission_classes([AllowAny])  # public QR
def create_payment_intent(request):
    data = request.data
    items = data.get("items", [])
    
    # Tính tổng giá trị order
    amount = sum(item['quantity'] * get_price(item['menu_item']) for item in items)

    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),  # amount in cents
        currency='usd',
        metadata={
            "table_code": data.get("table"),
            "items": str(items)
        },
    )
    return Response({"client_secret": intent.client_secret})