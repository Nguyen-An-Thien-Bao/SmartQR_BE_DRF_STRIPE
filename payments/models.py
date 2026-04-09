from django.db import models
from orders.models import Order

class Payment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    ]

    
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("stripe", "Stripe"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash"
    )

    stripe_payment_intent = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(max_length=10, default="usd")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.status}"