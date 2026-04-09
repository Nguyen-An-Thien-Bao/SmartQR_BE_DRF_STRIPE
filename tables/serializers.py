# tables/serializers.py
from rest_framework import serializers

from rbac.serializers import UserSerializer
from .models import Table


class TableSerializer(serializers.ModelSerializer):
    tenant_admin = UserSerializer(read_only = True)
    class Meta:
        model = Table
        fields = ["id", "name", "code", "is_active", "tenant_admin", "created_at", "updated_at"]
        read_only_fields = ["code", "tenant_admin"]

    def create(self, validated_data):
        request = self.context["request"]

        return Table.objects.create(
            tenant_admin=request.user,
            **validated_data
        )