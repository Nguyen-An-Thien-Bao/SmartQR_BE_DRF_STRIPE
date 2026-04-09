from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("tenantAdmin", "Tenant Admin"),
        ("waiter", "Waiter"),
        ("chef", "Chef")
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="tenantAdmin")
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=75, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="staff"
    )

    def __str__(self):
        return f"{self.role} - {self.email} - {self.username}"
    
    def get_tenant_admin(self):
        if self.role == "tenantAdmin":
            return self
        return self.created_by