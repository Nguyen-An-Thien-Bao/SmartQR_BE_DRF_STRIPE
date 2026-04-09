from rest_framework import serializers
from services.cloudinary_service import CloudinaryService
from .models import Category, MenuItem
from utils.get_tenant_from_request import get_tenant_from_request
from rbac.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    belong_to = UserSerializer(read_only=True)
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["belong_to", "slug"]

    def validate(self, data):
        request = self.context.get("request")
        tenant = get_tenant_from_request(request)

        if not tenant:
            return data

        name = data.get("name") or getattr(self.instance, "name", None)

        if Category.objects.filter(
            name=name,
            belong_to=tenant
        ).exclude(id=getattr(self.instance, "id", None)).exists():
            raise serializers.ValidationError("Category đã tồn tại")

        return data


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.ImageField(write_only=True, required=False)
    belong_to = UserSerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "price",
            "image",
            "image_url",
            "size",
            "description",
            "belong_to",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["created_at", "belong_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            tenant_admin = request.user  # hoặc get_tenant_admin()

            self.fields['category'].queryset = Category.objects.filter(
                belong_to=tenant_admin
            )

    def create(self, validated_data):
        image = validated_data.pop("image", None)

        if image:
            upload = CloudinaryService.upload_image(image)
            validated_data["image_url"] = upload["url"]
            validated_data["image_public_id"] = upload["public_id"]

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)

        if image:
            CloudinaryService.delete_image(instance.image_public_id)

            upload = CloudinaryService.upload_image(image)
            validated_data["image_url"] = upload["url"]
            validated_data["image_public_id"] = upload["public_id"]

        return super().update(instance, validated_data)

    def validate(self, data):
        request = self.context.get("request")
        tenant = get_tenant_from_request(request)

        if not tenant:
            return data

        category = data.get("category")

        if category and category.belong_to != tenant:
            raise serializers.ValidationError(
                "Category không thuộc tenant của bạn"
            )

        name = data.get("name") or getattr(self.instance, "name", None)
        size = data.get("size") or getattr(self.instance, "size", None)
        category = category or getattr(self.instance, "category", None)

        if MenuItem.objects.filter(
            name=name,
            size=size,
            category=category,
            belong_to=tenant
        ).exclude(id=getattr(self.instance, "id", None)).exists():
            raise serializers.ValidationError(
                "MenuItem đã tồn tại"
            )

        return data
    
class CategoryDetailSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "belong_to",
            "menu_items",
            "created_at",
            "updated_at"
        ]