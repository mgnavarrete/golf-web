from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    BusinessSettings,
    CashClosure,
    CourseEntry,
    PaymentMethod,
    RangeOrder,
)

User = get_user_model()


class CourseEntrySerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseEntry
        fields = [
            "id",
            "customer_name",
            "people_count",
            "amount_clp",
            "payment_method",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_name", "created_at", "updated_at"]

    def validate_people_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad de personas debe ser mayor a 0")
        return value

    def validate_amount_clp(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto no puede ser negativo")
        return value

    def get_created_by_name(self, obj):
        name = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return name or obj.created_by.email


class RangeOrderSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RangeOrder
        fields = [
            "id",
            "customer_name",
            "baskets_count",
            "unit_price_clp",
            "total_amount_clp",
            "payment_method",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_amount_clp", "created_by", "created_by_name", "created_at", "updated_at"]

    def validate_baskets_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad de canastos debe ser mayor a 0")
        return value

    def validate_unit_price_clp(self, value):
        if value <= 0:
            raise serializers.ValidationError("El valor unitario debe ser mayor a 0")
        return value

    def get_created_by_name(self, obj):
        name = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return name or obj.created_by.email


class BusinessSettingsSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BusinessSettings
        fields = ["default_range_unit_price_clp", "course_price_weekday_clp", "course_price_weekend_clp", "updated_by", "updated_by_name", "updated_at"]
        read_only_fields = ["updated_by", "updated_by_name", "updated_at"]

    def validate_default_range_unit_price_clp(self, value):
        if value <= 0:
            raise serializers.ValidationError("El valor unitario por defecto debe ser mayor a 0")
        return value

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return None
        name = f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return name or obj.updated_by.email


class CashClosureSerializer(serializers.ModelSerializer):
    closed_by_name = serializers.SerializerMethodField()
    reopened_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CashClosure
        fields = [
            "id",
            "operational_date",
            "scope",
            "status",
            "total_course_clp",
            "total_range_clp",
            "total_general_clp",
            "total_cash_clp",
            "total_card_clp",
            "total_transfer_clp",
            "total_other_clp",
            "total_people",
            "total_course_records",
            "total_range_orders",
            "total_baskets",
            "adjustment_clp",
            "notes",
            "per_user_totals",
            "closed_by",
            "closed_by_name",
            "closed_at",
            "reopened_by",
            "reopened_by_name",
            "reopened_at",
            "reopen_reason",
        ]

    def get_closed_by_name(self, obj):
        name = f"{obj.closed_by.first_name} {obj.closed_by.last_name}".strip()
        return name or obj.closed_by.email

    def get_reopened_by_name(self, obj):
        if not obj.reopened_by:
            return None
        name = f"{obj.reopened_by.first_name} {obj.reopened_by.last_name}".strip()
        return name or obj.reopened_by.email


class UserAdminSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "profile_icon",
            "role",
            "permission_overrides",
            "permissions",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    def get_permissions(self, obj):
        return obj.get_effective_permissions()


class UserAdminCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    profile_icon = serializers.IntegerField(required=False, min_value=1, max_value=10)
    role = serializers.ChoiceField(choices=[c[0] for c in User.ROLE_CHOICES], default=User.ROLE_MIXED)
    is_active = serializers.BooleanField(default=True)
    permission_overrides = serializers.DictField(required=False)


class UserAdminUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    profile_icon = serializers.IntegerField(required=False, min_value=1, max_value=10)
    role = serializers.ChoiceField(choices=[c[0] for c in User.ROLE_CHOICES], required=False)
    is_active = serializers.BooleanField(required=False)
    permission_overrides = serializers.DictField(required=False)


class ReportFiltersSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    record_type = serializers.ChoiceField(choices=["COURSE", "RANGE", "BOTH"], required=False)
    user_id = serializers.IntegerField(required=False)
    payment_method = serializers.ChoiceField(choices=[m[0] for m in PaymentMethod.choices], required=False)

    def validate(self, data):
        if data.get("date_from") and data.get("date_to") and data["date_from"] > data["date_to"]:
            raise serializers.ValidationError({"date_from": "La fecha inicial no puede ser mayor a la fecha final"})
        return data
