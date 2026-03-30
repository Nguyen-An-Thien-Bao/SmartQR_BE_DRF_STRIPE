from tables.models import Table

class TenantMixin:
    def get_tenant_admin(self):
        request = self.request
        user = request.user

        # Staff
        if user.is_authenticated:
            return user.get_tenant_admin()

        # Guest (QR)
        table_code = request.query_params.get("table_code")
        if table_code:
            try:
                table = Table.objects.get(code=table_code)
                return table.tenant_admin
            except Table.DoesNotExist:
                return None

        return None
    
    def get_base_queryset(self, model):
        user = self.request.user

        if user.is_superuser:
            return model.objects.all()

        tenant_admin = self.get_tenant_admin()

        if not tenant_admin:
            return model.objects.none()

        return model.objects.filter(belong_to=tenant_admin)