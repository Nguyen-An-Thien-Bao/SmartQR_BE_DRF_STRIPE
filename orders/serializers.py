from rest_framework import serializers
from orders.models import Order, OrderItem
from products.models import MenuItem
from tables.models import Table


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "price", "status", "chef"]
        read_only_fields = ["price", "chef"]

class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.role == "chef" and instance.chef is None:
            instance.chef = user
        return super().update(instance, validated_data)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "table", 
            "status",
            "payment_status",
            "total_price",
            "items",
            "created_at",
        ]
        read_only_fields = [
            "payment_status",
            "total_price",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            tenant_admin = request.user

            self.fields['table'].queryset = Table.objects.filter(
                tenant_admin=tenant_admin
            )

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context["request"]

        order = Order.objects.create(
            table=validated_data.get("table"),
            status="pending",
            payment_status="unpaid",
        )

        total_price = 0

        for item in items_data:
            menu_item = item["menu_item"]
            quantity = item["quantity"]
            price = menu_item.price

            total_price += price * quantity

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price
            )

        order.total_price = total_price
        order.save()

        return order