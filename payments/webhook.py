import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .services import PaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    print("WEBHOOK HIT")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        return HttpResponse(status=400)

    # PAYMENT SUCCESS
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]

        PaymentService.create_order_from_payment(intent)

    return HttpResponse(status=200)

