from rest_framework import serializers
from orders.models import Order, OrderItem
from products.models import MenuItem
from products.serializers import MenuItemSerializer
from rbac.serializers import UserSerializer
from tables.models import Table
from tables.serializers import TableSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    chef = UserSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "price", "status", "chef", "created_at", "updated_at"]
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
    
class OrderItemCreateSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ["menu_item", "quantity"] 

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    items_detail = OrderItemSerializer(source="items", many=True, read_only=True)
    # items = OrderItemCreateSerializer(many=True)
    table = serializers.SlugRelatedField(
        queryset=Table.objects.all(),
        slug_field="code",
        write_only=True
    )

    table_detail = TableSerializer(source="table", read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "table_detail",
            "status",
            "payment_status",
            "total_price",
            "items",
            "items_detail",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "payment_status",
            "total_price",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user

            if user.role == "tenantAdmin":
                tenant_admin = user
            elif user.role == "waiter":
                tenant_admin = user.created_by  # waiter

            self.fields['table'].queryset = Table.objects.filter(
                tenant_admin=tenant_admin
            )

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context["request"]

        order = Order.objects.create(
            table=validated_data.get("table"),
            status="processing",
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