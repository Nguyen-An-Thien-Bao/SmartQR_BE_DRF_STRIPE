from logs.models import Log

class LogMiddleware:
    ALLOWED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if response.status_code < 200 or response.status_code >= 300:
            return response

        if request.method not in self.ALLOWED_METHODS:
            return response

        if request.path.startswith("/admin") or request.path.startswith("/static"):
            return response

        user = request.user if request.user.is_authenticated else None

        if user:
            tenant = user.get_tenant_admin()

            Log.objects.create(
                user=user,
                tenant=tenant,
                action=request.method,
                message=f"{request.path}",
                endpoint=request.path,
                method=request.method,
                ip_address=self.get_ip(request),
                level=self.get_level(response.status_code)
            )

        return response

    def get_ip(self, request):
        return request.META.get('REMOTE_ADDR')

    def get_level(self, status_code):
        if status_code >= 500:
            return "ERROR"
        elif status_code >= 400:
            return "WARNING"
        return "INFO"