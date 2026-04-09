from django.contrib.auth.models import User
from rest_framework import serializers
from rbac.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom fields
        token["username"] = user.username
        token["role"] = user.role
        token["email"] = user.email

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    class Meta:
        model = User
        fields = ["id", "role", "username", "email", "password", "created_by"]

    def create(self, validated_data):
        request = self.context.get("request")

        created_by = validated_data.pop("created_by", None)
        role = validated_data.get("role", "tenantAdmin")

        if not request.user.is_authenticated:
            role = "tenantAdmin"

        user = User.objects.create_user(
            email=validated_data["email"],
            role=role,
            username=validated_data["username"],
            password=validated_data["password"]
        )

        if role == "tenantAdmin":
            user.created_by = None

        elif created_by and getattr(request.user, "id", None) == 1:
            user.created_by = created_by

        elif request.user.is_authenticated:
            user.created_by = request.user

        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "role", "username", "created_by", "email"]

    
class UserSerializerWithPassword(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    class Meta:
        model = User
        fields = ["id", "role", "username", "created_by", "email", "password", "created_at", "updated_at"]


    def update(self, instance, validated_data):
            password = validated_data.pop("password", None)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if password:
                instance.set_password(password)

            instance.save()
            return instance