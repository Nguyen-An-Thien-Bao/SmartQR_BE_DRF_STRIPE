from django.db import models
from rbac.models import User
import uuid

# Create your models here.

class Table(models.Model):
    name = models.CharField(max_length=100)   
    code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    tenant_admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tables",
        null=True,     
        blank=True     
    )  
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name