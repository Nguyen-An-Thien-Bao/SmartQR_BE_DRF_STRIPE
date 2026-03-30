from codecs import lookup

import django_filters
from .models import Product, ProductVariant

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["name"]

class ProductVariantFilter(django_filters.FilterSet):
    color = django_filters.CharFilter(field_name="color", lookup_expr="iexact")
    size = django_filters.CharFilter(field_name="size", lookup_expr="iexact")
    
    class Meta:
        model = ProductVariant
        fields = ["color", "size"]
