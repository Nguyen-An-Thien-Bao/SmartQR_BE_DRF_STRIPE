from rest_framework.permissions import BasePermission, SAFE_METHODS

class OwnerOrAdminPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        if user.is_superuser:
            return True

        if user.role == "admin":
            return obj.table.tenant_admin == user
        
        if user.role == "tenantAdmin":
            return obj.table.tenant_admin == user

        if user.role in ["staff", "chef"]:
            return obj.table.tenant_admin == user.created_by

        return obj.customer == user
    
class ReadOnlyOrAuthenticated(BasePermission):
    # GET: public, others needs to login
    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated
    

class IsAdminOrStaffOrReadOnly(BasePermission):
    # admin and staff have full permissions, other just read only
    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.role in ["tenantAdmin", "admin"]
        )
    

class IsTenantAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True

        return True  

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.is_superuser:
            return True
        
        tenant_admin = user.get_tenant_admin()
        
        obj_tenant_admin = getattr(obj, "tenant_admin", None)
        obj_belong_to = getattr(obj, "belong_to", None)

        # return obj.tenant_admin == user.get_tenant_admin() or obj.belong_to == user
        return (
            obj_tenant_admin == tenant_admin or obj_belong_to == tenant_admin
        )
    
class CanViewLogPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.role == "tenantAdmin":
            return True

        return False