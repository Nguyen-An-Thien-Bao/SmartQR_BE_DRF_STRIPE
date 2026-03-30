import stripe
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from orders.models import Order
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

# @api_view(['POST'])
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError:
#         return Response({"error": "Invalid payload"}, status=400)
#     except stripe.error.SignatureVerificationError:
#         return Response({"error": "Invalid signature"}, status=400)

#     # Xử lý event payment_intent.succeeded
#     if event['type'] == 'payment_intent.succeeded':
#         intent = event['data']['object']
#         payment_intent_id = intent['id']
#         metadata = intent.get('metadata', {})
#         order_id = metadata.get('order_id')

#         try:
#             payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)
#             payment.status = "succeeded"
#             payment.save()

#             # Update order
#             order = payment.order
#             order.payment_status = "paid"
#             order.paid_at = timezone.now()
#             order.save()
#         except Payment.DoesNotExist:
#             pass

#     return Response(status=200)

#  test Postman thì xài cái dưới
@api_view(['POST'])
def stripe_webhook(request):
    try:
        event = json.loads(request.body)
    except:
        return Response({"error": "Invalid payload"}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment_intent_id = intent['id']
        try:
            payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)
            payment.status = "succeeded"
            payment.save()

            order = payment.order
            order.payment_status = "paid"
            order.paid_at = timezone.now()
            order.save()
        except Payment.DoesNotExist:
            pass

    return Response(status=200)