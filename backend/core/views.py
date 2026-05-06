from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BusinessSettings,
    CashClosure,
    CourseEntry,
    PaymentMethod,
    RangeOrder,
    calculate_day_totals,
)
from .permissions import require_app_permission
from .serializers import (
    BusinessSettingsSerializer,
    CashClosureSerializer,
    CourseEntrySerializer,
    RangeOrderSerializer,
)

User = get_user_model()


def _local_today() -> date:
    return timezone.localtime().date()


def _parse_operational_date(value: str | None) -> date:
    if not value:
        return _local_today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError({"operational_date": "Formato inválido. Usa YYYY-MM-DD"}) from exc


def _day_bounds(operational_date: date):
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(operational_date, time.min), tz)
    end_dt = timezone.make_aware(datetime.combine(operational_date, time.max), tz)
    return start_dt, end_dt


def _date_filters(request):
    date_from = _parse_operational_date(request.query_params.get("date_from")) if request.query_params.get("date_from") else None
    date_to = _parse_operational_date(request.query_params.get("date_to")) if request.query_params.get("date_to") else None
    if date_from and date_to and date_from > date_to:
        raise ValidationError({"date_from": "La fecha inicial no puede ser mayor a la fecha final"})
    return date_from, date_to


def _is_scope_closed(operational_date: date, scope: str) -> bool:
    final_closed = CashClosure.objects.filter(
        operational_date=operational_date,
        scope=CashClosure.SCOPE_FINAL,
        status=CashClosure.STATUS_CLOSED,
    ).exists()
    if final_closed:
        return True

    return CashClosure.objects.filter(
        operational_date=operational_date,
        scope=scope,
        status=CashClosure.STATUS_CLOSED,
    ).exists()


def _assert_entry_mutation_allowed(model_instance_created_at, scope: str):
    operational_date = timezone.localtime(model_instance_created_at).date()
    if _is_scope_closed(operational_date, scope):
        raise ValidationError({"detail": "El día está cerrado para esta área"})


def _assert_creation_allowed(scope: str, operational_date: date | None = None):
    check_date = operational_date or _local_today()
    if _is_scope_closed(check_date, scope):
        raise ValidationError({"detail": "No se pueden crear registros: el día está cerrado"})


def _per_user_totals(operational_date: date):
    start_dt, end_dt = _day_bounds(operational_date)

    user_map = defaultdict(lambda: {"course_clp": 0, "range_clp": 0, "total_clp": 0})

    course_rows = (
        CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .values("created_by", "created_by__email", "created_by__first_name", "created_by__last_name")
        .annotate(total=Sum("amount_clp"))
    )

    range_rows = (
        RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .values("created_by", "created_by__email", "created_by__first_name", "created_by__last_name")
        .annotate(total=Sum("total_amount_clp"))
    )

    for row in course_rows:
        key = str(row["created_by"])
        full_name = f"{row['created_by__first_name']} {row['created_by__last_name']}".strip()
        user_map[key].update({
            "user_id": row["created_by"],
            "email": row["created_by__email"],
            "name": full_name or row["created_by__email"],
        })
        user_map[key]["course_clp"] = int(row["total"] or 0)

    for row in range_rows:
        key = str(row["created_by"])
        full_name = f"{row['created_by__first_name']} {row['created_by__last_name']}".strip()
        user_map[key].update({
            "user_id": row["created_by"],
            "email": row["created_by__email"],
            "name": full_name or row["created_by__email"],
        })
        user_map[key]["range_clp"] = int(row["total"] or 0)

    for item in user_map.values():
        item["total_clp"] = int(item.get("course_clp", 0) + item.get("range_clp", 0))

    return list(user_map.values())


class CourseEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseEntrySerializer

    def get_queryset(self):
        require_app_permission(self.request, "can_manage_course_entries")
        qs = CourseEntry.objects.select_related("created_by")

        date_from, date_to = _date_filters(self.request)
        if date_from:
            start_dt, _ = _day_bounds(date_from)
            qs = qs.filter(created_at__gte=start_dt)
        if date_to:
            _, end_dt = _day_bounds(date_to)
            qs = qs.filter(created_at__lte=end_dt)

        user_id = self.request.query_params.get("user_id")
        payment_method = self.request.query_params.get("payment_method")
        if user_id:
            qs = qs.filter(created_by_id=user_id)
        if payment_method:
            qs = qs.filter(payment_method=payment_method)

        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        require_app_permission(self.request, "can_manage_course_entries")
        _assert_creation_allowed(CashClosure.SCOPE_COURSE)
        serializer.save(created_by=self.request.user)


class CourseEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseEntrySerializer
    queryset = CourseEntry.objects.select_related("created_by")

    def get_object(self):
        require_app_permission(self.request, "can_manage_course_entries")
        return super().get_object()

    def perform_update(self, serializer):
        if not self.request.user.has_app_permission("can_edit_course_entries") and not self.request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para editar registros de cancha"})
        _assert_entry_mutation_allowed(self.get_object().created_at, CashClosure.SCOPE_COURSE)
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.has_app_permission("can_delete_course_entries") and not self.request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para eliminar registros de cancha"})
        _assert_entry_mutation_allowed(instance.created_at, CashClosure.SCOPE_COURSE)
        instance.delete()


class RangeOrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RangeOrderSerializer

    def get_queryset(self):
        require_app_permission(self.request, "can_manage_range_orders")
        qs = RangeOrder.objects.select_related("created_by")

        date_from, date_to = _date_filters(self.request)
        if date_from:
            start_dt, _ = _day_bounds(date_from)
            qs = qs.filter(created_at__gte=start_dt)
        if date_to:
            _, end_dt = _day_bounds(date_to)
            qs = qs.filter(created_at__lte=end_dt)

        user_id = self.request.query_params.get("user_id")
        payment_method = self.request.query_params.get("payment_method")
        if user_id:
            qs = qs.filter(created_by_id=user_id)
        if payment_method:
            qs = qs.filter(payment_method=payment_method)

        return qs.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        require_app_permission(request, "can_manage_range_orders")
        _assert_creation_allowed(CashClosure.SCOPE_RANGE)

        payload = request.data.copy()
        if not payload.get("unit_price_clp"):
            payload["unit_price_clp"] = BusinessSettings.get_solo().default_range_unit_price_clp

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RangeOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RangeOrderSerializer
    queryset = RangeOrder.objects.select_related("created_by")

    def get_object(self):
        require_app_permission(self.request, "can_manage_range_orders")
        return super().get_object()

    def perform_update(self, serializer):
        if not self.request.user.has_app_permission("can_edit_range_orders") and not self.request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para editar pedidos de range"})
        _assert_entry_mutation_allowed(self.get_object().created_at, CashClosure.SCOPE_RANGE)
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.has_app_permission("can_delete_range_orders") and not self.request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para eliminar pedidos de range"})
        _assert_entry_mutation_allowed(instance.created_at, CashClosure.SCOPE_RANGE)
        instance.delete()


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_view_dashboard")
        operational_date = _parse_operational_date(request.query_params.get("operational_date"))

        totals = calculate_day_totals(operational_date)
        latest_course = CourseEntry.objects.select_related("created_by").order_by("-created_at")[:5]
        latest_range = RangeOrder.objects.select_related("created_by").order_by("-created_at")[:5]

        return Response(
            {
                "operational_date": str(operational_date),
                **totals,
                "latest_course_entries": CourseEntrySerializer(latest_course, many=True).data,
                "latest_range_orders": RangeOrderSerializer(latest_range, many=True).data,
            }
        )


class CashClosuresStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_close_day")
        operational_date = _parse_operational_date(request.query_params.get("operational_date"))

        closures = CashClosure.objects.filter(
            operational_date=operational_date,
            status=CashClosure.STATUS_CLOSED,
        ).order_by("scope")
        data = {
            "operational_date": str(operational_date),
            "closures": CashClosureSerializer(closures, many=True).data,
            "can_close_course": not _is_scope_closed(operational_date, CashClosure.SCOPE_COURSE),
            "can_close_range": not _is_scope_closed(operational_date, CashClosure.SCOPE_RANGE),
            "can_close_final": not _is_scope_closed(operational_date, CashClosure.SCOPE_FINAL),
        }
        return Response(data)


class CashCloseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        require_app_permission(request, "can_close_day")

        scope = request.data.get("scope")
        if scope not in [CashClosure.SCOPE_COURSE, CashClosure.SCOPE_RANGE, CashClosure.SCOPE_FINAL]:
            raise ValidationError({"scope": "Debes indicar COURSE, RANGE o FINAL"})

        operational_date = _parse_operational_date(request.data.get("operational_date"))
        notes = request.data.get("notes", "")
        adjustment_clp = int(request.data.get("adjustment_clp", 0) or 0)

        if scope == CashClosure.SCOPE_COURSE and request.user.role not in [User.ROLE_ADMIN, User.ROLE_COURSE, User.ROLE_MIXED] and not request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para cerrar cancha"})
        if scope == CashClosure.SCOPE_RANGE and request.user.role not in [User.ROLE_ADMIN, User.ROLE_RANGE, User.ROLE_MIXED] and not request.user.is_superuser:
            raise ValidationError({"detail": "No tienes permiso para cerrar range"})
        if scope == CashClosure.SCOPE_FINAL and request.user.role != User.ROLE_ADMIN and not request.user.is_superuser:
            raise ValidationError({"detail": "Solo Admin puede generar el cierre final"})

        existing = CashClosure.objects.filter(
            operational_date=operational_date,
            scope=scope,
            status=CashClosure.STATUS_CLOSED,
        ).first()
        if existing:
            raise ValidationError({"detail": "Este cierre ya fue generado"})

        if scope == CashClosure.SCOPE_FINAL:
            for required_scope in [CashClosure.SCOPE_COURSE, CashClosure.SCOPE_RANGE]:
                if not CashClosure.objects.filter(
                    operational_date=operational_date,
                    scope=required_scope,
                    status=CashClosure.STATUS_CLOSED,
                ).exists():
                    raise ValidationError({"detail": "Debes cerrar cancha y range antes del cierre final"})

        totals = calculate_day_totals(operational_date)
        totals["total_general_clp"] += adjustment_clp

        # Limpia cierres legacy reabiertos para mantener flujo único de cierre activo.
        CashClosure.objects.filter(
            operational_date=operational_date,
            scope=scope,
        ).exclude(status=CashClosure.STATUS_CLOSED).delete()

        closure = CashClosure.objects.create(
            operational_date=operational_date,
            scope=scope,
            adjustment_clp=adjustment_clp,
            notes=notes,
            status=CashClosure.STATUS_CLOSED,
            closed_by=request.user,
            per_user_totals=_per_user_totals(operational_date),
            **totals,
        )

        return Response(CashClosureSerializer(closure).data, status=status.HTTP_201_CREATED)


class CashReopenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        require_app_permission(request, "can_reopen_closure")

        scope = request.data.get("scope")
        if scope not in [CashClosure.SCOPE_COURSE, CashClosure.SCOPE_RANGE, CashClosure.SCOPE_FINAL]:
            raise ValidationError({"scope": "Debes indicar COURSE, RANGE o FINAL"})

        operational_date = _parse_operational_date(request.data.get("operational_date"))
        try:
            closure = CashClosure.objects.get(
                operational_date=operational_date,
                scope=scope,
                status=CashClosure.STATUS_CLOSED,
            )
        except CashClosure.DoesNotExist as exc:
            raise ValidationError({"detail": "No existe cierre cerrado para esa fecha y área"}) from exc

        deleted_scopes: list[str] = [scope]
        closure.delete()

        if scope in [CashClosure.SCOPE_COURSE, CashClosure.SCOPE_RANGE]:
            final = CashClosure.objects.filter(
                operational_date=operational_date,
                scope=CashClosure.SCOPE_FINAL,
                status=CashClosure.STATUS_CLOSED,
            ).first()
            if final:
                final.delete()
                deleted_scopes.append(CashClosure.SCOPE_FINAL)

        return Response(
            {
                "operational_date": str(operational_date),
                "deleted_scopes": deleted_scopes,
                "detail": "Cierre reabierto correctamente",
            }
        )


class BusinessSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings_obj = BusinessSettings.get_solo()
        return Response(BusinessSettingsSerializer(settings_obj).data)

    def patch(self, request):
        require_app_permission(request, "can_patch_settings")
        settings_obj = BusinessSettings.get_solo()
        serializer = BusinessSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(updated_by=request.user)
        return Response(BusinessSettingsSerializer(updated).data)


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_view_reports")

        date_from, date_to = _date_filters(request)
        if not date_from:
            date_from = _local_today()
        if not date_to:
            date_to = _local_today()

        start_dt, _ = _day_bounds(date_from)
        _, end_dt = _day_bounds(date_to)

        user_id = request.query_params.get("user_id")
        payment_method = request.query_params.get("payment_method")
        record_type = request.query_params.get("record_type", "BOTH")

        course_qs = CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        range_qs = RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)

        if user_id:
            course_qs = course_qs.filter(created_by_id=user_id)
            range_qs = range_qs.filter(created_by_id=user_id)
        if payment_method:
            course_qs = course_qs.filter(payment_method=payment_method)
            range_qs = range_qs.filter(payment_method=payment_method)

        if record_type == "COURSE":
            range_qs = range_qs.none()
        elif record_type == "RANGE":
            course_qs = course_qs.none()

        total_course = int(course_qs.aggregate(v=Sum("amount_clp"))["v"] or 0)
        total_range = int(range_qs.aggregate(v=Sum("total_amount_clp"))["v"] or 0)

        by_day = []
        current = date_from
        while current <= date_to:
            sdt, edt = _day_bounds(current)
            by_day.append(
                {
                    "date": str(current),
                    "course_total_clp": int(course_qs.filter(created_at__gte=sdt, created_at__lte=edt).aggregate(v=Sum("amount_clp"))["v"] or 0),
                    "range_total_clp": int(range_qs.filter(created_at__gte=sdt, created_at__lte=edt).aggregate(v=Sum("total_amount_clp"))["v"] or 0),
                    "people_count": int(course_qs.filter(created_at__gte=sdt, created_at__lte=edt).aggregate(v=Sum("people_count"))["v"] or 0),
                    "baskets_count": int(range_qs.filter(created_at__gte=sdt, created_at__lte=edt).aggregate(v=Sum("baskets_count"))["v"] or 0),
                }
            )
            current = current + timedelta(days=1)

        payment_totals = {
            "CASH": 0,
            "CARD": 0,
            "TRANSFER": 0,
            "OTHER": 0,
        }
        for method in payment_totals.keys():
            payment_totals[method] = int(
                (course_qs.filter(payment_method=method).aggregate(v=Sum("amount_clp"))["v"] or 0)
                + (range_qs.filter(payment_method=method).aggregate(v=Sum("total_amount_clp"))["v"] or 0)
            )

        return Response(
            {
                "filters": {
                    "date_from": str(date_from),
                    "date_to": str(date_to),
                    "record_type": record_type,
                    "user_id": int(user_id) if user_id else None,
                    "payment_method": payment_method,
                },
                "totals": {
                    "course_clp": total_course,
                    "range_clp": total_range,
                    "general_clp": total_course + total_range,
                    "people_count": int(course_qs.aggregate(v=Sum("people_count"))["v"] or 0),
                    "baskets_count": int(range_qs.aggregate(v=Sum("baskets_count"))["v"] or 0),
                    "course_records": course_qs.count(),
                    "range_records": range_qs.count(),
                },
                "payment_totals": payment_totals,
                "series": {
                    "by_day": by_day,
                },
            }
        )


class ReportsRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_view_reports")

        date_from, date_to = _date_filters(request)
        if not date_from:
            date_from = _local_today()
        if not date_to:
            date_to = _local_today()

        start_dt, _ = _day_bounds(date_from)
        _, end_dt = _day_bounds(date_to)

        user_id = request.query_params.get("user_id")
        payment_method = request.query_params.get("payment_method")
        record_type = request.query_params.get("record_type", "BOTH")

        response = {}

        if record_type in ["COURSE", "BOTH"]:
            course_qs = CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
            if user_id:
                course_qs = course_qs.filter(created_by_id=user_id)
            if payment_method:
                course_qs = course_qs.filter(payment_method=payment_method)
            response["course_entries"] = CourseEntrySerializer(course_qs.order_by("-created_at"), many=True).data

        if record_type in ["RANGE", "BOTH"]:
            range_qs = RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
            if user_id:
                range_qs = range_qs.filter(created_by_id=user_id)
            if payment_method:
                range_qs = range_qs.filter(payment_method=payment_method)
            response["range_orders"] = RangeOrderSerializer(range_qs.order_by("-created_at"), many=True).data

        closures_qs = CashClosure.objects.filter(
            operational_date__gte=date_from,
            operational_date__lte=date_to,
            status=CashClosure.STATUS_CLOSED,
        ).order_by("-operational_date", "scope")
        response["closures"] = CashClosureSerializer(closures_qs, many=True).data
        return Response(response)


class ExportXlsxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_export_excel")

        try:
            import xlsxwriter
        except Exception as exc:  # pragma: no cover
            raise ValidationError({"detail": "Dependencia xlsxwriter no disponible"}) from exc

        date_from, date_to = _date_filters(request)
        if not date_from:
            date_from = _local_today()
        if not date_to:
            date_to = _local_today()

        start_dt, _ = _day_bounds(date_from)
        _, end_dt = _day_bounds(date_to)

        course_qs = CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
        range_qs = RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt).select_related("created_by")
        closures_qs = CashClosure.objects.filter(
            operational_date__gte=date_from,
            operational_date__lte=date_to,
            status=CashClosure.STATUS_CLOSED,
        )

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True, "remove_timezone": True})

        date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd"})
        ws_course = workbook.add_worksheet("Cancha")
        headers_course = [
            "Fecha",
            "Hora",
            "Nombre",
            "Cantidad de personas",
            "Valor cobrado",
            "Método de pago",
            "Usuario",
            "Notas",
        ]
        for col, h in enumerate(headers_course):
            ws_course.write(0, col, h)

        for row, item in enumerate(course_qs, start=1):
            local_dt = timezone.localtime(item.created_at)
            user_name = f"{item.created_by.first_name} {item.created_by.last_name}".strip() or item.created_by.email
            ws_course.write_datetime(row, 0, local_dt, date_fmt)
            ws_course.write(row, 1, local_dt.strftime("%H:%M"))
            ws_course.write(row, 2, item.customer_name)
            ws_course.write_number(row, 3, item.people_count)
            ws_course.write_number(row, 4, item.amount_clp)
            ws_course.write(row, 5, item.get_payment_method_display())
            ws_course.write(row, 6, user_name)
            ws_course.write(row, 7, item.notes or "")

        ws_range = workbook.add_worksheet("Range")
        headers_range = [
            "Fecha",
            "Hora",
            "Nombre",
            "Cantidad de canastos",
            "Valor unitario",
            "Total cobrado",
            "Método de pago",
            "Usuario",
            "Notas",
        ]
        for col, h in enumerate(headers_range):
            ws_range.write(0, col, h)

        for row, item in enumerate(range_qs, start=1):
            local_dt = timezone.localtime(item.created_at)
            user_name = f"{item.created_by.first_name} {item.created_by.last_name}".strip() or item.created_by.email
            ws_range.write_datetime(row, 0, local_dt, date_fmt)
            ws_range.write(row, 1, local_dt.strftime("%H:%M"))
            ws_range.write(row, 2, item.customer_name)
            ws_range.write_number(row, 3, item.baskets_count)
            ws_range.write_number(row, 4, item.unit_price_clp)
            ws_range.write_number(row, 5, item.total_amount_clp)
            ws_range.write(row, 6, item.get_payment_method_display())
            ws_range.write(row, 7, user_name)
            ws_range.write(row, 8, item.notes or "")

        ws_closure = workbook.add_worksheet("Cierres")
        headers_closure = [
            "Fecha",
            "Scope",
            "Total cancha",
            "Total range",
            "Total general",
            "Total efectivo",
            "Total tarjeta",
            "Total transferencia",
            "Usuario que cerró",
            "Observaciones",
            "Estado",
        ]
        for col, h in enumerate(headers_closure):
            ws_closure.write(0, col, h)

        for row, item in enumerate(closures_qs, start=1):
            user_name = f"{item.closed_by.first_name} {item.closed_by.last_name}".strip() or item.closed_by.email
            ws_closure.write_datetime(row, 0, datetime.combine(item.operational_date, time.min), date_fmt)
            ws_closure.write(row, 1, item.scope)
            ws_closure.write_number(row, 2, item.total_course_clp)
            ws_closure.write_number(row, 3, item.total_range_clp)
            ws_closure.write_number(row, 4, item.total_general_clp)
            ws_closure.write_number(row, 5, item.total_cash_clp)
            ws_closure.write_number(row, 6, item.total_card_clp)
            ws_closure.write_number(row, 7, item.total_transfer_clp)
            ws_closure.write(row, 8, user_name)
            ws_closure.write(row, 9, item.notes or "")
            ws_closure.write(row, 10, item.status)

        workbook.close()
        output.seek(0)

        filename = f"golf-export-{date_from}-{date_to}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class ExportPdfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_app_permission(request, "can_export_excel")

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas
        except Exception as exc:  # pragma: no cover
            raise ValidationError({"detail": "Dependencia reportlab no disponible"}) from exc

        operational_date = _parse_operational_date(request.query_params.get("operational_date"))
        totals = calculate_day_totals(operational_date)
        closures = CashClosure.objects.filter(
            operational_date=operational_date,
            status=CashClosure.STATUS_CLOSED,
        ).order_by("scope")

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 20 * mm
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(20 * mm, y, "Resumen Diario - Caja Golf")

        y -= 10 * mm
        pdf.setFont("Helvetica", 11)
        pdf.drawString(20 * mm, y, f"Fecha operativa: {operational_date}")

        y -= 10 * mm
        lines = [
            f"Total cancha: ${totals['total_course_clp']}",
            f"Total range: ${totals['total_range_clp']}",
            f"Total general: ${totals['total_general_clp']}",
            f"Personas cancha: {totals['total_people']}",
            f"Canastos vendidos: {totals['total_baskets']}",
            f"Métodos de pago - Efectivo: ${totals['total_cash_clp']}, Tarjeta: ${totals['total_card_clp']}, Transferencia: ${totals['total_transfer_clp']}, Otro: ${totals['total_other_clp']}",
        ]

        for line in lines:
            pdf.drawString(20 * mm, y, line)
            y -= 7 * mm

        y -= 4 * mm
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20 * mm, y, "Cierres registrados")
        y -= 8 * mm

        pdf.setFont("Helvetica", 10)
        if not closures:
            pdf.drawString(20 * mm, y, "No hay cierres generados para esta fecha")
        else:
            for closure in closures:
                user_name = f"{closure.closed_by.first_name} {closure.closed_by.last_name}".strip() or closure.closed_by.email
                line = f"{closure.scope} | {closure.status} | total ${closure.total_general_clp} | usuario {user_name}"
                pdf.drawString(20 * mm, y, line)
                y -= 6 * mm
                if y <= 20 * mm:
                    pdf.showPage()
                    y = height - 20 * mm
                    pdf.setFont("Helvetica", 10)

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="golf-resumen-{operational_date}.pdf"'
        return response
