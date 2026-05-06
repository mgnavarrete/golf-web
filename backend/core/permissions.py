from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)


class HasAppPermission(BasePermission):
    permission_key = ""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        if user.is_superuser:
            return True
        key = getattr(view, "required_permission", self.permission_key)
        if not key:
            return True
        return user.has_app_permission(key)


class CanManageUsers(HasAppPermission):
    permission_key = "can_manage_users"


class CanViewDashboard(HasAppPermission):
    permission_key = "can_view_dashboard"


class CanManageCourseEntries(HasAppPermission):
    permission_key = "can_manage_course_entries"


class CanManageRangeOrders(HasAppPermission):
    permission_key = "can_manage_range_orders"


class CanViewReports(HasAppPermission):
    permission_key = "can_view_reports"


class CanExportExcel(HasAppPermission):
    permission_key = "can_export_excel"


class CanCloseDay(HasAppPermission):
    permission_key = "can_close_day"


class CanReopenClosure(HasAppPermission):
    permission_key = "can_reopen_closure"


def require_app_permission(request, key: str):
    user = request.user
    if not (user and user.is_authenticated and user.is_active):
        raise PermissionDenied("Debes iniciar sesión")
    if user.is_superuser:
        return
    if not user.has_app_permission(key):
        raise PermissionDenied("No tienes permisos para esta acción")
