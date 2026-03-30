from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Log(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.TextField()

    endpoint = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=10, null=True, blank=True)

    level = models.CharField(
        choices=[('INFO','INFO'), ('WARNING','WARNING'), ('ERROR','ERROR')],
        default='INFO'
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action}"