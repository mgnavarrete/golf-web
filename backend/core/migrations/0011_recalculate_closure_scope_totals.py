from datetime import datetime, time

from django.db import migrations
from django.db.models import Sum
from django.utils import timezone


TOTAL_FIELDS = [
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
]

PAYMENT_METHOD_SUM_FIELDS = {
    "CASH": "total_cash_clp",
    "CARD": "total_card_clp",
    "TRANSFER": "total_transfer_clp",
    "OTHER": "total_other_clp",
}


def empty_totals():
    return {field: 0 for field in TOTAL_FIELDS}


def day_bounds(operational_date):
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(operational_date, time.min), tz)
    end_dt = timezone.make_aware(datetime.combine(operational_date, time.max), tz)
    return start_dt, end_dt


def calculate_totals(CourseEntry, RangeOrder, operational_date, scope):
    start_dt, end_dt = day_bounds(operational_date)
    include_course = scope in ["COURSE", "FINAL"]
    include_range = scope in ["RANGE", "FINAL"]

    course_qs = (
        CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        if include_course
        else CourseEntry.objects.none()
    )
    range_qs = (
        RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        if include_range
        else RangeOrder.objects.none()
    )

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

    total_course_clp = int(course_qs.aggregate(value=Sum("amount_clp"))["value"] or 0)
    total_range_clp = int(range_qs.aggregate(value=Sum("total_amount_clp"))["value"] or 0)
    return {
        "total_course_clp": total_course_clp,
        "total_range_clp": total_range_clp,
        "total_general_clp": total_course_clp + total_range_clp,
        "total_people": int(course_qs.aggregate(value=Sum("people_count"))["value"] or 0),
        "total_course_records": course_qs.count(),
        "total_range_orders": range_qs.count(),
        "total_baskets": int(range_qs.aggregate(value=Sum("baskets_count"))["value"] or 0),
        **payment_totals,
    }


def combine_totals(course_totals, range_totals, adjustment_clp):
    totals = empty_totals()
    for source in [course_totals, range_totals]:
        for field in TOTAL_FIELDS:
            if field == "total_general_clp":
                continue
            totals[field] += int(source.get(field, 0) or 0)
    totals["total_general_clp"] = totals["total_course_clp"] + totals["total_range_clp"] + int(adjustment_clp or 0)
    return totals


def per_user_totals(CourseEntry, RangeOrder, operational_date, scope):
    start_dt, end_dt = day_bounds(operational_date)
    user_map = {}

    def ensure_user(row):
        key = str(row["created_by"])
        if key not in user_map:
            full_name = f"{row['created_by__first_name']} {row['created_by__last_name']}".strip()
            user_map[key] = {
                "user_id": row["created_by"],
                "email": row["created_by__email"],
                "name": full_name or row["created_by__email"],
                "course_clp": 0,
                "range_clp": 0,
                "total_clp": 0,
            }
        return user_map[key]

    if scope in ["COURSE", "FINAL"]:
        course_rows = (
            CourseEntry.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
            .values("created_by", "created_by__email", "created_by__first_name", "created_by__last_name")
            .annotate(total=Sum("amount_clp"))
        )
        for row in course_rows:
            ensure_user(row)["course_clp"] = int(row["total"] or 0)

    if scope in ["RANGE", "FINAL"]:
        range_rows = (
            RangeOrder.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
            .values("created_by", "created_by__email", "created_by__first_name", "created_by__last_name")
            .annotate(total=Sum("total_amount_clp"))
        )
        for row in range_rows:
            ensure_user(row)["range_clp"] = int(row["total"] or 0)

    for item in user_map.values():
        item["total_clp"] = int(item["course_clp"] + item["range_clp"])
    return list(user_map.values())


def recalculate_closure_scope_totals(apps, schema_editor):
    CashClosure = apps.get_model("core", "CashClosure")
    CourseEntry = apps.get_model("core", "CourseEntry")
    RangeOrder = apps.get_model("core", "RangeOrder")

    cache = {}

    def get_day_totals(operational_date):
        if operational_date not in cache:
            course_totals = calculate_totals(CourseEntry, RangeOrder, operational_date, "COURSE")
            range_totals = calculate_totals(CourseEntry, RangeOrder, operational_date, "RANGE")
            cache[operational_date] = {
                "COURSE": course_totals,
                "RANGE": range_totals,
            }
        return cache[operational_date]

    for closure in CashClosure.objects.all().iterator():
        day_totals = get_day_totals(closure.operational_date)
        if closure.scope == "COURSE":
            totals = day_totals["COURSE"]
        elif closure.scope == "RANGE":
            totals = day_totals["RANGE"]
        elif closure.scope == "FINAL":
            totals = combine_totals(day_totals["COURSE"], day_totals["RANGE"], closure.adjustment_clp)
        else:
            continue

        for field, value in totals.items():
            setattr(closure, field, value)
        closure.per_user_totals = per_user_totals(CourseEntry, RangeOrder, closure.operational_date, closure.scope)
        closure.save(update_fields=[*TOTAL_FIELDS, "per_user_totals"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_user_options_and_more"),
    ]

    operations = [
        migrations.RunPython(recalculate_closure_scope_totals, migrations.RunPython.noop),
    ]
