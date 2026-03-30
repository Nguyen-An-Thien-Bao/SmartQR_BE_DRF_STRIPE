from django.shortcuts import render
from rest_framework import generics
from config.permissions import OwnerOrAdminPermission
from orders.models import Order, OrderItem
from orders.serializers import OrderItemSerializer, OrderItemUpdateSerializer, OrderSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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

        if user.role in ["staff", "chef"]:
            return Order.objects.filter(
                table__tenant_admin=user.created_by
            )

        return Order.objects.none()
    
class OrderItemListView(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return OrderItem.objects.all()

        # Tenant Admin → thấy tất cả OrderItem thuộc order table của mình
        if user.role == "tenantAdmin":
            return OrderItem.objects.filter(
                order__table__tenant_admin=user
            )

        # Staff (Chef hoặc Waiter) → thấy OrderItem thuộc TenantAdmin của họ
        if user.role in ["chef", "waiter"]:
            return OrderItem.objects.filter(
                order__table__tenant_admin=user.created_by
            )

        # Các role khác → không thấy
        return OrderItem.objects.none()

class OrderItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OrderItemUpdateSerializer
        return OrderItemSerializer
    
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