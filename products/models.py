from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True)

    belong_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["name", "belong_to"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
    ]

    name = models.CharField(max_length=100)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    belong_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["name", "size", "category", "belong_to"]

    def __str__(self):
        return f"{self.name} ({self.size})"