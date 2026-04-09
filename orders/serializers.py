from django.utils import timezone

from rest_framework import serializers
import stripe
from orders.models import Order, OrderItem
from payments.models import Payment
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

    # def create(self, validated_data):
    #     items_data = validated_data.pop("items")
    #     request = self.context["request"]

    #     order = Order.objects.create(
    #         table=validated_data.get("table"),
    #         status="processing",
    #         payment_status="unpaid",
    #     )

    #     total_price = 0

    #     for item in items_data:
    #         menu_item = item["menu_item"]
    #         quantity = item["quantity"]
    #         price = menu_item.price

    #         total_price += price * quantity

    #         OrderItem.objects.create(
    #             order=order,
    #             menu_item=menu_item,
    #             quantity=quantity,
    #             price=price
    #         )

    #     order.total_price = total_price
    #     order.save()

    #     return order

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        table = validated_data.get("table")
        method = validated_data.get("method", "cash")

        # --- Tạo Order ---
        order = Order.objects.create(
            table=table,
            status="processing",
            payment_status="unpaid",
            total_price=0
        )

        total_price = 0
        for item in items_data:
            menu_item = item["menu_item"]
            quantity = item["quantity"]
            price = menu_item.price
            total_price += price * quantity
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity, price=price)

        order.total_price = total_price
        order.save()

        # --- Tạo Payment object ---
        if method == "cash":
            payment = Payment.objects.create(
                order=order,
                method="cash",
                amount=total_price,
                status="succeeded",  # cash thì coi là thanh toán ngay
                currency="usd",
            )
            order.payment_status = "paid"
            order.paid_at = timezone.now()
            order.save()
        elif method == "stripe":
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY

            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),
                currency="usd",
                metadata={"order_id": str(order.id)},
            )

            payment = Payment.objects.create(
                order=order,
                method="stripe",
                amount=total_price,
                stripe_payment_intent=intent.id,
                status="pending",
                currency="usd",
            )

            order.stripe_session_id = intent.id
            order.save()

        return order

    def get_items_detail(self, obj):
        return [{"menu_item": i.menu_item.name, "quantity": i.quantity, "price": i.price} for i in obj.items.all()]