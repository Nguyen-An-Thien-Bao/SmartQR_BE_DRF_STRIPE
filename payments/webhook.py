import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from orders.models import Order, OrderItem
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        table_code = intent['metadata']['table_code']
        items = json.loads(intent['metadata']['items'])

        # Tạo Order
        order = Order.objects.create(
            table_code=table_code,
            payment_status='paid'
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                menu_item_id=item['menu_item'],
                quantity=item['quantity']
            )
        # Tạo Payment record
        Payment.objects.create(
            order=order,
            amount=intent['amount_received']/100,
            status='paid',
            stripe_payment_intent=intent['id']
        )
    
    return HttpResponse(status=200)