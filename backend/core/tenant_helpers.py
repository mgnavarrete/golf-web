"""Compatibilidad legacy: multi-tenant removido (empresa única)."""


def get_active_company_from_request(request):
    return None


def require_active_company(request):
    return None


def user_can_access_company(user, company):
    return True


def get_user_companies(user):
    return []
