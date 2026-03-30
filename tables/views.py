from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Table
from .serializers import TableSerializer
from config.permissions import IsTenantAdminOrReadOnly


class TableViewSet(ModelViewSet):
    queryset = Table.objects.all()  
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated, IsTenantAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Table.objects.all()
        
        return Table.objects.filter(
            tenant_admin=user.get_tenant_admin()
        )