from tables.models import Table

def get_tenant_from_request(request):
    if not request:
        return None

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