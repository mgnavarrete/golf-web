# Generated manually to replace legacy security domain with golf cash domain.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_edgedevice_company_edgedevice_latitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="permission_overrides",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Admin"),
                    ("COURSE", "Cancha"),
                    ("RANGE", "Range"),
                    ("MIXED", "Mixto"),
                ],
                default="MIXED",
                max_length=20,
            ),
        ),
        migrations.RemoveField(
            model_name="user",
            name="default_company",
        ),
        migrations.CreateModel(
            name="BusinessSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("default_range_unit_price_clp", models.PositiveIntegerField(default=5000)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_business_settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "business_settings",
            },
        ),
        migrations.CreateModel(
            name="CourseEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=180)),
                ("people_count", models.PositiveIntegerField()),
                ("amount_clp", models.PositiveIntegerField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CASH", "Efectivo"),
                            ("CARD", "Tarjeta"),
                            ("TRANSFER", "Transferencia"),
                            ("OTHER", "Otro"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="course_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "course_entry",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="RangeOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=180)),
                ("baskets_count", models.PositiveIntegerField()),
                ("unit_price_clp", models.PositiveIntegerField()),
                ("total_amount_clp", models.PositiveIntegerField(default=0)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CASH", "Efectivo"),
                            ("CARD", "Tarjeta"),
                            ("TRANSFER", "Transferencia"),
                            ("OTHER", "Otro"),
                        ],
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="range_orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "range_order",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CashClosure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("operational_date", models.DateField()),
                (
                    "scope",
                    models.CharField(
                        choices=[("COURSE", "Cancha"), ("RANGE", "Range"), ("FINAL", "Final")],
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("CLOSED", "Cerrado"), ("REOPENED", "Reabierto")],
                        default="CLOSED",
                        max_length=10,
                    ),
                ),
                ("total_course_clp", models.PositiveIntegerField(default=0)),
                ("total_range_clp", models.PositiveIntegerField(default=0)),
                ("total_general_clp", models.PositiveIntegerField(default=0)),
                ("total_cash_clp", models.PositiveIntegerField(default=0)),
                ("total_card_clp", models.PositiveIntegerField(default=0)),
                ("total_transfer_clp", models.PositiveIntegerField(default=0)),
                ("total_other_clp", models.PositiveIntegerField(default=0)),
                ("total_people", models.PositiveIntegerField(default=0)),
                ("total_course_records", models.PositiveIntegerField(default=0)),
                ("total_range_orders", models.PositiveIntegerField(default=0)),
                ("total_baskets", models.PositiveIntegerField(default=0)),
                ("adjustment_clp", models.IntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                ("per_user_totals", models.JSONField(blank=True, default=dict)),
                ("closed_at", models.DateTimeField(auto_now_add=True)),
                ("reopened_at", models.DateTimeField(blank=True, null=True)),
                ("reopen_reason", models.TextField(blank=True)),
                (
                    "closed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="closures_closed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reopened_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="closures_reopened",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "cash_closure",
                "ordering": ["-operational_date", "scope"],
                "unique_together": {("operational_date", "scope")},
            },
        ),
        migrations.AddIndex(
            model_name="courseentry",
            index=models.Index(fields=["created_at"], name="course_entr_created_8849b5_idx"),
        ),
        migrations.AddIndex(
            model_name="courseentry",
            index=models.Index(fields=["payment_method"], name="course_entr_payment_f6f4ef_idx"),
        ),
        migrations.AddIndex(
            model_name="courseentry",
            index=models.Index(fields=["created_by"], name="course_entr_created_4b8057_idx"),
        ),
        migrations.AddIndex(
            model_name="rangeorder",
            index=models.Index(fields=["created_at"], name="range_orde_created_4f65c1_idx"),
        ),
        migrations.AddIndex(
            model_name="rangeorder",
            index=models.Index(fields=["payment_method"], name="range_orde_payment_4d0702_idx"),
        ),
        migrations.AddIndex(
            model_name="rangeorder",
            index=models.Index(fields=["created_by"], name="range_orde_created_4f24cc_idx"),
        ),
        migrations.AddIndex(
            model_name="cashclosure",
            index=models.Index(fields=["operational_date", "scope"], name="cash_closu_operati_f0ef45_idx"),
        ),
        migrations.AddIndex(
            model_name="cashclosure",
            index=models.Index(fields=["status"], name="cash_closu_status_65db1f_idx"),
        ),
        migrations.DeleteModel(name="UserCompanyMembership"),
        migrations.DeleteModel(name="Report"),
        migrations.DeleteModel(name="AlertEvent"),
        migrations.DeleteModel(name="EdgeDevice"),
        migrations.DeleteModel(name="AlertType"),
        migrations.DeleteModel(name="Camera"),
        migrations.DeleteModel(name="Company"),
    ]
