# tables/serializers.py
from rest_framework import serializers
from .models import Table


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ["id", "name", "code", "is_active", "tenant_admin"]
        read_only_fields = ["code", "tenant_admin"]

    def create(self, validated_data):
        request = self.context["request"]

        return Table.objects.create(
            tenant_admin=request.user,
            **validated_data
        )