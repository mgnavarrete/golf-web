from django.urls import path

from .views import (
    BusinessSettingsView,
    CashCloseView,
    CashClosureDetailView,
    CashClosuresStatusView,
    CashReopenView,
    CourseEntryDetailView,
    CourseEntryListCreateView,
    DashboardSummaryView,
    ExportPdfView,
    ExportXlsxView,
    RangeOrderDetailView,
    RangeOrderListCreateView,
    ReportsRecordsView,
    ReportsSummaryView,
)
from .views_users import user_detail, user_list_create

urlpatterns = [
    path("course-entries/", CourseEntryListCreateView.as_view(), name="course_entries"),
    path("course-entries/<int:pk>/", CourseEntryDetailView.as_view(), name="course_entry_detail"),
    path("range-orders/", RangeOrderListCreateView.as_view(), name="range_orders"),
    path("range-orders/<int:pk>/", RangeOrderDetailView.as_view(), name="range_order_detail"),
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard_summary"),
    path("closures/status/", CashClosuresStatusView.as_view(), name="closures_status"),
    path("closures/<int:pk>/detail/", CashClosureDetailView.as_view(), name="closure_detail"),
    path("closures/close/", CashCloseView.as_view(), name="closures_close"),
    path("closures/reopen/", CashReopenView.as_view(), name="closures_reopen"),
    path("reports/summary/", ReportsSummaryView.as_view(), name="reports_summary"),
    path("reports/records/", ReportsRecordsView.as_view(), name="reports_records"),
    path("exports/xlsx/", ExportXlsxView.as_view(), name="export_xlsx"),
    path("exports/pdf/", ExportPdfView.as_view(), name="export_pdf"),
    path("business-settings/", BusinessSettingsView.as_view(), name="business_settings"),
    path("users/", user_list_create, name="users"),
    path("users/<int:pk>/", user_detail, name="user_detail"),
]
