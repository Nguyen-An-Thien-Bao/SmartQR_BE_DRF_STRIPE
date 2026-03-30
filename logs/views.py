from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from config.permissions import CanViewLogPermission
from logs.models import Log
from logs.serializers import LogSerializer

# Create your views here.
class LogViewSet(ModelViewSet):
    queryset = Log.objects.all().order_by("-created_at")
    serializer_class = LogSerializer
    permission_classes = [CanViewLogPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Log.objects.all()

        if user.role == "tenantAdmin":
            return Log.objects.filter(tenant=user)

        return Log.objects.none()