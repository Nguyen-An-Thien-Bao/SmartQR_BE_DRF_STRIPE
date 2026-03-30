from urllib import request

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def EndpointList(request):
    return Response({
        "name": "Bi Nhe Store",
        "version": "v1",
        "admin": "/admin/",
        "docs": "/docs/",
        "products": "/api/products/",
        "menu-items": "/api/products/menu-items",
        "categories": "/api/products/categories",
        "orders": "/api/orders/",
        "orderItems": "/api/orders/items",
        "users": "/api/users/",
        "tables": "/api/tables/",
        "payments": "/api/payments/",
    })