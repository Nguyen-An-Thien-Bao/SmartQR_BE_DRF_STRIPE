from rest_framework import serializers

from orders.serializers import OrderSerializer
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["status", "stripe_payment_intent"]