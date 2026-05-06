from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime, time
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.ROLE_ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_COURSE = "COURSE"
    ROLE_RANGE = "RANGE"
    ROLE_MIXED = "MIXED"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_COURSE, "Cancha"),
        (ROLE_RANGE, "Range"),
        (ROLE_MIXED, "Mixto"),
    ]

    username = None
    email = models.EmailField(unique=True)
    profile_icon = models.IntegerField(default=1, help_text="Icono de perfil (1-10)")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MIXED)
    permission_overrides = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "core_user"

    def clean(self):
        super().clean()
        if self.profile_icon and (self.profile_icon < 1 or self.profile_icon > 10):
            raise ValidationError({"profile_icon": "El icono debe estar entre 1 y 10"})

    @staticmethod
    def base_permissions_for_role(role: str) -> dict[str, bool]:
        templates = {
            User.ROLE_ADMIN: {
                "can_view_dashboard": True,
                "can_manage_course_entries": True,
                "can_manage_range_orders": True,
                "can_view_reports": True,
                "can_export_excel": True,
                "can_close_day": True,
                "can_manage_users": True,
                "can_edit_course_entries": True,
                "can_delete_course_entries": True,
                "can_edit_range_orders": True,
                "can_delete_range_orders": True,
                "can_reopen_closure": True,
                "can_patch_settings": True,
            },
            User.ROLE_COURSE: {
                "can_view_dashboard": True,
                "can_manage_course_entries": True,
                "can_manage_range_orders": False,
                "can_view_reports": False,
                "can_export_excel": False,
                "can_close_day": True,
                "can_manage_users": False,
                "can_edit_course_entries": True,
                "can_delete_course_entries": False,
                "can_edit_range_orders": False,
                "can_delete_range_orders": False,
                "can_reopen_closure": False,
                "can_patch_settings": False,
            },
            User.ROLE_RANGE: {
                "can_view_dashboard": True,
                "can_manage_course_entries": False,
                "can_manage_range_orders": True,
                "can_view_reports": False,
                "can_export_excel": False,
                "can_close_day": True,
                "can_manage_users": False,
                "can_edit_course_entries": False,
                "can_delete_course_entries": False,
                "can_edit_range_orders": True,
                "can_delete_range_orders": False,
                "can_reopen_closure": False,
                "can_patch_settings": False,
            },
            User.ROLE_MIXED: {
                "can_view_dashboard": True,
                "can_manage_course_entries": True,
                "can_manage_range_orders": True,
                "can_view_reports": True,
                "can_export_excel": False,
                "can_close_day": True,
                "can_manage_users": False,
                "can_edit_course_entries": True,
                "can_delete_course_entries": False,
                "can_edit_range_orders": True,
                "can_delete_range_orders": False,
                "can_reopen_closure": False,
                "can_patch_settings": False,
            },
        }
        return dict(templates.get(role, templates[User.ROLE_MIXED]))

    def get_effective_permissions(self) -> dict[str, bool]:
        permissions = self.base_permissions_for_role(self.role)
        overrides = self.permission_overrides or {}
        for key, value in overrides.items():
            if key in permissions and isinstance(value, bool):
                permissions[key] = value

        if self.is_superuser:
            for key in permissions.keys():
                permissions[key] = True
        return permissions

    def has_app_permission(self, key: str) -> bool:
        return self.get_effective_permissions().get(key, False)

    def __str__(self):
        return self.email


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Efectivo"
    CARD = "CARD", "Tarjeta"
    TRANSFER = "TRANSFER", "Transferencia"
    OTHER = "OTHER", "Otro"


class CourseEntry(models.Model):
    customer_name = models.CharField(max_length=180)
    people_count = models.PositiveIntegerField()
    amount_clp = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="course_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_entry"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.customer_name} ({self.people_count})"


class BusinessSettings(models.Model):
    default_range_unit_price_clp = models.PositiveIntegerField(default=5000)
    course_price_weekday_clp = models.PositiveIntegerField(default=20000)
    course_price_weekend_clp = models.PositiveIntegerField(default=25000)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_business_settings",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "business_settings"

    @classmethod
    def get_solo(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance

    def __str__(self):
        return "Configuración de negocio"


class RangeOrder(models.Model):
    customer_name = models.CharField(max_length=180)
    baskets_count = models.PositiveIntegerField()
    unit_price_clp = models.PositiveIntegerField()
    total_amount_clp = models.PositiveIntegerField(default=0)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="range_orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "range_order"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["created_by"]),
        ]

    def clean(self):
        if self.baskets_count <= 0:
            raise ValidationError({"baskets_count": "La cantidad de canastos debe ser mayor a 0"})

    def save(self, *args, **kwargs):
        self.total_amount_clp = int(self.baskets_count) * int(self.unit_price_clp)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_name} ({self.baskets_count} canastos)"


class CashClosure(models.Model):
    SCOPE_COURSE = "COURSE"
    SCOPE_RANGE = "RANGE"
    SCOPE_FINAL = "FINAL"

    SCOPE_CHOICES = [
        (SCOPE_COURSE, "Cancha"),
        (SCOPE_RANGE, "Range"),
        (SCOPE_FINAL, "Final"),
    ]

    STATUS_CLOSED = "CLOSED"
    STATUS_REOPENED = "REOPENED"
    STATUS_CHOICES = [
        (STATUS_CLOSED, "Cerrado"),
        (STATUS_REOPENED, "Reabierto"),
    ]

    operational_date = models.DateField()
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_CLOSED)

    total_course_clp = models.PositiveIntegerField(default=0)
    total_range_clp = models.PositiveIntegerField(default=0)
    total_general_clp = models.PositiveIntegerField(default=0)

    total_cash_clp = models.PositiveIntegerField(default=0)
    total_card_clp = models.PositiveIntegerField(default=0)
    total_transfer_clp = models.PositiveIntegerField(default=0)
    total_other_clp = models.PositiveIntegerField(default=0)

    total_people = models.PositiveIntegerField(default=0)
    total_course_records = models.PositiveIntegerField(default=0)
    total_range_orders = models.PositiveIntegerField(default=0)
    total_baskets = models.PositiveIntegerField(default=0)

    adjustment_clp = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    per_user_totals = models.JSONField(default=dict, blank=True)

    closed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="closures_closed")
    closed_at = models.DateTimeField(auto_now_add=True)

    reopened_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closures_reopened",
    )
    reopened_at = models.DateTimeField(null=True, blank=True)
    reopen_reason = models.TextField(blank=True)

    class Meta:
        db_table = "cash_closure"
        ordering = ["-operational_date", "scope"]
        unique_together = [["operational_date", "scope"]]
        indexes = [
            models.Index(fields=["operational_date", "scope"]),
            models.Index(fields=["status"]),
        ]

    @property
    def is_closed(self) -> bool:
        return self.status == self.STATUS_CLOSED

    def reopen(self, user: User, reason: str):
        self.status = self.STATUS_REOPENED
        self.reopened_by = user
        self.reopened_at = timezone.now()
        self.reopen_reason = reason
        self.save(update_fields=["status", "reopened_by", "reopened_at", "reopen_reason"])

    def __str__(self):
        return f"{self.operational_date} - {self.scope} ({self.status})"


PAYMENT_METHOD_SUM_FIELDS = {
    PaymentMethod.CASH: "total_cash_clp",
    PaymentMethod.CARD: "total_card_clp",
    PaymentMethod.TRANSFER: "total_transfer_clp",
    PaymentMethod.OTHER: "total_other_clp",
}


def calculate_day_totals(operational_date):
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(operational_date, time.min), tz)
    end_dt = timezone.make_aware(datetime.combine(operational_date, time.max), tz)

    course_qs = CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
    range_qs = RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)

    payment_totals = {
        "total_cash_clp": 0,
        "total_card_clp": 0,
        "total_transfer_clp": 0,
        "total_other_clp": 0,
    }

    for method, field_name in PAYMENT_METHOD_SUM_FIELDS.items():
        course_total = course_qs.filter(payment_method=method).aggregate(value=Sum("amount_clp"))["value"] or 0
        range_total = range_qs.filter(payment_method=method).aggregate(value=Sum("total_amount_clp"))["value"] or 0
        payment_totals[field_name] = int(course_total + range_total)

    total_course_clp = course_qs.aggregate(value=Sum("amount_clp"))["value"] or 0
    total_range_clp = range_qs.aggregate(value=Sum("total_amount_clp"))["value"] or 0

    return {
        "total_course_clp": int(total_course_clp),
        "total_range_clp": int(total_range_clp),
        "total_general_clp": int(total_course_clp + total_range_clp),
        "total_people": int(course_qs.aggregate(value=Sum("people_count"))["value"] or 0),
        "total_course_records": course_qs.count(),
        "total_range_orders": range_qs.count(),
        "total_baskets": int(range_qs.aggregate(value=Sum("baskets_count"))["value"] or 0),
        **payment_totals,
    }
