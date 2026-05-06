from django.utils.deprecation import MiddlewareMixin


class NoopMiddleware(MiddlewareMixin):
    """Middleware placeholder (multi-tenant removido)."""

    def process_request(self, request):
        return None
