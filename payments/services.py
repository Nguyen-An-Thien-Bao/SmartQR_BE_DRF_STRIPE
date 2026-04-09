import uuid
import uuid
import stripe
import json
from django.conf import settings
from orders.models import Order, OrderItem
from products.models import MenuItem
from tables.models import Table
from .models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:

    @staticmethod
    def calculate_total(items):
        total = 0

        for item in items:
            menu_item = MenuItem.objects.get(id=item["menu_item"])
            total += menu_item.price * item["quantity"]

        return total

    # CREATE STRIPE PAYMENT INTENT
    @staticmethod
    def create_payment_intent(table, items):
        total = PaymentService.calculate_total(items)

        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency="usd",
            metadata={
                "table_code": table,
                "items": json.dumps(items)  # ✅ double quotes chuẩn JSON
            }
        )

        return intent

    # CREATE ORDER AFTER PAYMENT SUCCESS
    @staticmethod
    def create_order_from_payment(intent):
        print("SERVICE START")

        # Lấy metadata an toàn từ StripeObject
        metadata = intent.get("metadata", {})

        if not isinstance(metadata, dict):
            print("INVALID METADATA:", metadata)
            return None

        print("METADATA RAW:", metadata)

        table_code = metadata.get("table")
        items_raw = metadata.get("items")

        # Nếu thiếu metadata → stop
        if not table_code or not items_raw:
            print("MISSING METADATA:", table_code, items_raw)
            return None

        # Parse items JSON an toàn
        try:
            items = json.loads(items_raw)
        except Exception as e:
            print("JSON ERROR:", str(e))
            return None

        print("PARSED ITEMS:", items)

        # Prevent duplicate payment
        intent_id = intent.get("id")
        if Payment.objects.filter(stripe_payment_intent=intent_id).exists():
            print("⚠️ DUPLICATE PAYMENT:", intent_id)
            return None

        # Lấy table
        try:
            table_uuid = uuid.UUID(table_code)
            table_obj = Table.objects.get(code=table_uuid)
        except Exception as e:
            print("TABLE ERROR:", str(e))
            return None

        # Tạo Order
        order = Order.objects.create(
            table=table_obj,
            payment_status="paid",
            status="processing"
        )

        total_price = 0

        # Tạo OrderItem
        for item in items:
            try:
                menu_item = MenuItem.objects.get(id=item["menu_item"])
                quantity = item["quantity"]
                price = menu_item.price
            except Exception as e:
                print("ITEM ERROR:", str(e))
                continue  # bỏ item lỗi, không crash toàn bộ

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=price
            )

            total_price += price * quantity

        # Nếu không có item hợp lệ → rollback
        if total_price == 0:
            print("EMPTY ORDER → DELETE")
            order.delete()
            return None

        # Update total
        order.total_price = total_price
        order.save()

        # Tạo Payment record
        try:
            Payment.objects.create(
                order=order,
                amount=total_price,
                stripe_payment_intent=intent_id,
                status="succeeded",
                method="stripe"
            )
        except Exception as e:
            print("PAYMENT SAVE ERROR:", str(e))
            order.delete()
            return None

        print("ORDER CREATED:", order.id)

        return order