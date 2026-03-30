from rest_framework import generics
from .models import Category, MenuItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
)
from config.permissions import IsTenantAdminOrReadOnly
from rest_framework.viewsets import ModelViewSet
from config.pagination import DefaultPagination
from .mixins import TenantMixin


class CategoryListCreateView(TenantMixin, generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsTenantAdminOrReadOnly]

    def get_queryset(self):
        return self.get_base_queryset(Category)

    def perform_create(self, serializer):
        serializer.save(belong_to=self.get_tenant_admin())


class CategoryDetailView(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsTenantAdminOrReadOnly]

    def get_queryset(self):
        return self.get_base_queryset(Category)
    
class MenuItemListCreateView(TenantMixin, generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsTenantAdminOrReadOnly]

    def get_queryset(self):
        return self.get_base_queryset(MenuItem)

    def perform_create(self, serializer):
        serializer.save(belong_to=self.get_tenant_admin())


class MenuItemDetailView(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsTenantAdminOrReadOnly]

    def get_queryset(self):
        return self.get_base_queryset(MenuItem)