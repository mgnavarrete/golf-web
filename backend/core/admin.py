from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import BusinessSettings, CashClosure, CourseEntry, RangeOrder, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("id",)
    list_display = ("id", "email", "first_name", "last_name", "role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "profile_icon")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "permission_overrides",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(CourseEntry)
class CourseEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "people_count", "amount_clp", "payment_method", "created_by", "created_at")
    list_filter = ("payment_method", "created_at")
    search_fields = ("customer_name", "created_by__email")


@admin.register(RangeOrder)
class RangeOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "baskets_count",
        "unit_price_clp",
        "total_amount_clp",
        "payment_method",
        "created_by",
        "created_at",
    )
    list_filter = ("payment_method", "created_at")
    search_fields = ("customer_name", "created_by__email")


@admin.register(CashClosure)
class CashClosureAdmin(admin.ModelAdmin):
    list_display = ("operational_date", "scope", "status", "total_general_clp", "closed_by", "closed_at")
    list_filter = ("scope", "status", "operational_date")
    search_fields = ("closed_by__email",)


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ("default_range_unit_price_clp", "updated_by", "updated_at")
