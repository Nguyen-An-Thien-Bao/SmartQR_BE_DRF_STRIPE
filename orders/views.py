from django.shortcuts import render
from requests import Response
from rest_framework import generics
from config.permissions import OwnerOrAdminPermission
from orders.models import Order, OrderItem
from orders.serializers import OrderItemSerializer, OrderItemUpdateSerializer, OrderSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter]
    search_fields = ["table__name", "payment_status", "status"]

    def get_queryset(self):
        user = self.request.user
        try:
            if user.is_superuser:
                return Order.objects.all()

            if user.role == "tenantAdmin":
                return Order.objects.filter(
                    table__tenant_admin=user
                )

            if user.role in ["waiter", "chef"]:
                return Order.objects.filter(
                    table__tenant_admin=user.created_by
                )
            return Order.objects.none()
            
        except:
            return Order.objects.none()


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OwnerOrAdminPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Order.objects.all()

        if user.role == "admin":
            return Order.objects.filter(
                table__tenant_admin=user
            )

        if user.role == "tenantAdmin":
            return Order.objects.filter(table__tenant_admin=user)

        if user.role in ["staff", "chef"]:
            return Order.objects.filter(
                table__tenant_admin=user.created_by
            )

        return Order.objects.none()
    
class OrderItemListView(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["menu_item__name", "status", "chef__username"]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return OrderItem.objects.all()

        if user.role == "tenantAdmin":
            return OrderItem.objects.filter(
                order__table__tenant_admin=user
            )

        if user.role in ["chef", "waiter"]:
            return OrderItem.objects.filter(
                order__table__tenant_admin=user.created_by
            )

        return OrderItem.objects.none()


class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OrderItemUpdateSerializer
        return OrderItemSerializer
    
    def destroy(self, request, *args, **kwargs):
        user = request.user

        if user.role == "chef":
            return Response(
                {"error": "Chef cannot delete order item"},
                status=403
            )

        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return OrderItem.objects.all()

        if user.role == "tenantAdmin":
            return OrderItem.objects.filter(
                order__table__tenant_admin=user
            )

        if user.role in ["chef", "waiter"]:
            return OrderItem.objects.filter(
                order__table__tenant_admin=user.created_by
            )

        return OrderItem.objects.none()