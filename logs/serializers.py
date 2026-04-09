from rest_framework import serializers

from logs.models import Log
from rbac.serializers import UserSerializer

class LogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = UserSerializer(read_only=True)
    class Meta:
        model = Log
        fields = "__all__"