from rest_framework import serializers
from rbac.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "role", "username", "email", "password"]

    def create(self, validated_data):
        request = self.context["request"]

        if not request.user.is_authenticated:
            validated_data["role"] = "tenantAdmin"

        user = User.objects.create_user(
            email=validated_data["email"],
            role=validated_data["role"],
            username=validated_data["username"],
            password=validated_data["password"]
        )

        if request.user.is_authenticated:
            user.created_by = request.user
            user.save()

        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "role", "username", "created_by", "email", "password"]