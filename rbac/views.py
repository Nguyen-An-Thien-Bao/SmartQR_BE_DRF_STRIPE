from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from config.permissions import IsAdminOrStaffOrReadOnly, IsTenantAdminOrReadOnly
from rbac.models import User
from rbac.serializers import RegisterSerializer, UserSerializer

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsTenantAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        if user.is_superuser:
            return User.objects.all()

        if user.role == "tenantAdmin":
            return User.objects.filter(
                created_by=user
            ) | User.objects.filter(
                id=user.id
            )

        return User.objects.filter(id=user.id)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]