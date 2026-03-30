from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariant
import random


class Command(BaseCommand):
    help = "Seed database with sample products"

    def handle(self, *args, **kwargs):

        self.stdout.write("Deleting old data...")
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Creating categories...")

        categories = [
            "T-Shirt",
            "Hoodie",
            "Jacket",
            "Sweater"
        ]

        category_objects = []

        for name in categories:
            category = Category.objects.create(categoryName=name)
            category_objects.append(category)

        self.stdout.write("Creating products...")

        materials = ["Cotton", "Polyester", "Wool", "Denim"]
        colors = ["Black", "White", "Red", "Blue", "Green"]
        sizes = ["S", "M", "L", "XL"]

        products = []

        for i in range(10):
            product = Product.objects.create(
                name=f"Product {i+1}",
                price=random.randint(10, 100),
                material=random.choice(materials),
                category=random.choice(category_objects)
            )
            products.append(product)

        self.stdout.write("Creating product variants...")

        for product in products:
            for size in sizes:
                for color in random.sample(colors, 3):

                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        color=color,
                        in_stock=random.randint(0, 50),
                        description=f"{product.name} - {size} - {color}"
                    )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))