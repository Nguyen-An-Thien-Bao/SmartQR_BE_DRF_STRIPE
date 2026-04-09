from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView, Response
from services.cloudinary_service import CloudinaryService
from tables.models import Table
from .models import Category, MenuItem
from .serializers import (
    CategoryDetailSerializer,
    CategorySerializer,
    MenuItemSerializer,
)
from config.permissions import IsTenantAdminOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from config.pagination import DefaultPagination
from .mixins import TenantMixin


class CategoryListCreateView(TenantMixin, generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsTenantAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return self.get_base_queryset(Category)

    def perform_create(self, serializer):
        serializer.save(belong_to=self.get_tenant_admin())

class CategoryMenuItemListCreateView(TenantMixin, generics.ListAPIView):
    serializer_class = CategoryDetailSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name__menu_items__name']

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
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return self.get_base_queryset(MenuItem)

    def perform_create(self, serializer):
        serializer.save(belong_to=self.get_tenant_admin())


class MenuItemDetailView(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsTenantAdminOrReadOnly]

    def get_queryset(self):
        return self.get_base_queryset(MenuItem)
    
    def perform_destroy(self, instance):
        try:
            CloudinaryService.delete_image(instance.image_public_id)
        except:
            pass

        instance.delete()


class PublicMenuView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        try:
            table = Table.objects.get(code=code)
        except Table.DoesNotExist:
            return Response({"error": "Table not found"}, status=404)

        tenant_admin = table.tenant_admin

        categories = Category.objects.filter(belong_to=tenant_admin)
        menu_items = MenuItem.objects.filter(belong_to=tenant_admin)

        return Response({
            "categories": CategorySerializer(categories, many=True).data,
            "menu_items": MenuItemSerializer(menu_items, many=True).data
        })