from django.db import models
from rbac.models import User
from products.models import MenuItem
from tables.models import Table


class Order(models.Model):

    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("Done", "Done"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    table = models.ForeignKey(
        Table,
        to_field="code",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.table.name}"


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("done", "Done"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0 
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    chef = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"role": "chef"})
    

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.order.items.filter(status__in=["pending", "preparing"]).exists():
            self.order.status = "processing"
        else:
            self.order.status = "done"
        self.order.save()