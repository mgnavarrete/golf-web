from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import BusinessSettings, CashClosure, CourseEntry, PaymentMethod, RangeOrder

User = get_user_model()


class GolfFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role=User.ROLE_ADMIN,
            is_staff=True,
        )
        self.admin.permission_overrides = {
            "can_export_excel": True,
            "can_reopen_closure": True,
            "can_patch_settings": True,
            "can_manage_users": True,
        }
        self.admin.save()

        self.mixed = User.objects.create_user(
            email="mixed@test.com",
            password="testpass123",
            role=User.ROLE_MIXED,
        )
        self.reopener = User.objects.create_user(
            email="reopener@test.com",
            password="testpass123",
            role=User.ROLE_MIXED,
            permission_overrides={"can_reopen_closure": True},
        )

    def test_range_total_is_calculated(self):
        order = RangeOrder.objects.create(
            customer_name="Cliente",
            baskets_count=3,
            unit_price_clp=5000,
            payment_method=PaymentMethod.CASH,
            created_by=self.mixed,
        )
        self.assertEqual(order.total_amount_clp, 15000)

    def _create_daily_records(self):
        CourseEntry.objects.create(
            customer_name="Jugador 1",
            people_count=2,
            amount_clp=20000,
            payment_method=PaymentMethod.CARD,
            created_by=self.mixed,
        )
        CourseEntry.objects.create(
            customer_name="Jugador 2",
            people_count=1,
            amount_clp=10000,
            payment_method=PaymentMethod.CASH,
            created_by=self.mixed,
        )
        RangeOrder.objects.create(
            customer_name="Range 1",
            baskets_count=3,
            unit_price_clp=5000,
            payment_method=PaymentMethod.CASH,
            created_by=self.mixed,
        )
        RangeOrder.objects.create(
            customer_name="Range 2",
            baskets_count=2,
            unit_price_clp=6000,
            payment_method=PaymentMethod.TRANSFER,
            created_by=self.mixed,
        )

    def test_course_and_range_closures_store_scope_only(self):
        self._create_daily_records()
        self.client.force_authenticate(user=self.admin)

        course = self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_COURSE, "operational_date": str(date.today())},
            format="json",
        )
        self.assertEqual(course.status_code, 201)
        self.assertEqual(course.data["total_course_clp"], 30000)
        self.assertEqual(course.data["total_range_clp"], 0)
        self.assertEqual(course.data["total_general_clp"], 30000)
        self.assertEqual(course.data["total_people"], 3)
        self.assertEqual(course.data["total_baskets"], 0)
        self.assertEqual(course.data["total_cash_clp"], 10000)
        self.assertEqual(course.data["total_card_clp"], 20000)
        self.assertEqual(course.data["total_transfer_clp"], 0)

        range_response = self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_RANGE, "operational_date": str(date.today())},
            format="json",
        )
        self.assertEqual(range_response.status_code, 201)
        self.assertEqual(range_response.data["total_course_clp"], 0)
        self.assertEqual(range_response.data["total_range_clp"], 27000)
        self.assertEqual(range_response.data["total_general_clp"], 27000)
        self.assertEqual(range_response.data["total_people"], 0)
        self.assertEqual(range_response.data["total_baskets"], 5)
        self.assertEqual(range_response.data["total_cash_clp"], 15000)
        self.assertEqual(range_response.data["total_transfer_clp"], 12000)

    def test_final_closure_requires_partials_and_sums_saved_closures(self):
        self._create_daily_records()
        self.client.force_authenticate(user=self.admin)

        blocked = self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_FINAL, "operational_date": str(date.today())},
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

        self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_COURSE, "operational_date": str(date.today())},
            format="json",
        )
        still_blocked = self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_FINAL, "operational_date": str(date.today())},
            format="json",
        )
        self.assertEqual(still_blocked.status_code, 400)

        self.client.post(
            "/api/closures/close/",
            {"scope": CashClosure.SCOPE_RANGE, "operational_date": str(date.today())},
            format="json",
        )
        status_response = self.client.get("/api/closures/status/", {"operational_date": str(date.today())})
        self.assertEqual(status_response.status_code, 200)
        self.assertTrue(status_response.data["can_close_final"])

        final = self.client.post(
            "/api/closures/close/",
            {
                "scope": CashClosure.SCOPE_FINAL,
                "operational_date": str(date.today()),
                "adjustment_clp": 1000,
            },
            format="json",
        )
        self.assertEqual(final.status_code, 201)
        self.assertEqual(final.data["total_course_clp"], 30000)
        self.assertEqual(final.data["total_range_clp"], 27000)
        self.assertEqual(final.data["total_general_clp"], 58000)
        self.assertEqual(final.data["total_cash_clp"], 25000)
        self.assertEqual(final.data["total_card_clp"], 20000)
        self.assertEqual(final.data["total_transfer_clp"], 12000)

    def test_reports_records_returns_only_final_closures(self):
        self._create_daily_records()
        self.client.force_authenticate(user=self.admin)
        self.client.post("/api/closures/close/", {"scope": CashClosure.SCOPE_COURSE}, format="json")
        self.client.post("/api/closures/close/", {"scope": CashClosure.SCOPE_RANGE}, format="json")
        self.client.post("/api/closures/close/", {"scope": CashClosure.SCOPE_FINAL}, format="json")

        response = self.client.get(
            "/api/reports/records/",
            {
                "date_from": str(date.today()),
                "date_to": str(date.today()),
                "record_type": "NONE",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["closures"]), 1)
        self.assertEqual(response.data["closures"][0]["scope"], CashClosure.SCOPE_FINAL)

    def test_partial_closures_do_not_block_other_scope_records(self):
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_COURSE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )

        self.client.force_authenticate(user=self.mixed)
        range_created = self.client.post(
            "/api/range-orders/",
            {
                "customer_name": "Permitido Range",
                "baskets_count": 1,
                "unit_price_clp": 5000,
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )
        self.assertEqual(range_created.status_code, 201)

        CashClosure.objects.all().delete()
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_RANGE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )
        course_created = self.client.post(
            "/api/course-entries/",
            {
                "customer_name": "Permitido Cancha",
                "people_count": 1,
                "amount_clp": 10000,
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )
        self.assertEqual(course_created.status_code, 201)

    def test_closure_blocks_new_records(self):
        CourseEntry.objects.create(
            customer_name="A",
            people_count=2,
            amount_clp=20000,
            payment_method=PaymentMethod.CARD,
            created_by=self.mixed,
        )

        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_COURSE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )

        self.client.force_authenticate(user=self.mixed)
        response = self.client.post(
            "/api/course-entries/",
            {
                "customer_name": "Bloqueado",
                "people_count": 1,
                "amount_clp": 10000,
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_business_settings_singleton(self):
        one = BusinessSettings.get_solo()
        two = BusinessSettings.get_solo()
        self.assertEqual(one.id, two.id)

    def test_reopen_course_deletes_course_and_final(self):
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_COURSE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_FINAL,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )

        self.client.force_authenticate(user=self.reopener)
        response = self.client.post(
            "/api/closures/reopen/",
            {
                "scope": CashClosure.SCOPE_COURSE,
                "operational_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted_scopes"], [CashClosure.SCOPE_COURSE, CashClosure.SCOPE_FINAL])
        self.assertFalse(
            CashClosure.objects.filter(
                operational_date=date.today(),
                scope=CashClosure.SCOPE_COURSE,
                status=CashClosure.STATUS_CLOSED,
            ).exists()
        )
        self.assertFalse(
            CashClosure.objects.filter(
                operational_date=date.today(),
                scope=CashClosure.SCOPE_FINAL,
                status=CashClosure.STATUS_CLOSED,
            ).exists()
        )

    def test_reopen_requires_permission(self):
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_RANGE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )
        self.client.force_authenticate(user=self.mixed)
        response = self.client.post(
            "/api/closures/reopen/",
            {
                "scope": CashClosure.SCOPE_RANGE,
                "operational_date": str(date.today()),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_reopen_unblocks_new_course_records(self):
        CashClosure.objects.create(
            operational_date=date.today(),
            scope=CashClosure.SCOPE_COURSE,
            status=CashClosure.STATUS_CLOSED,
            closed_by=self.admin,
        )

        self.client.force_authenticate(user=self.mixed)
        blocked = self.client.post(
            "/api/course-entries/",
            {
                "customer_name": "Bloqueado",
                "people_count": 1,
                "amount_clp": 10000,
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)

        self.client.force_authenticate(user=self.reopener)
        reopened = self.client.post(
            "/api/closures/reopen/",
            {
                "scope": CashClosure.SCOPE_COURSE,
                "operational_date": str(date.today()),
            },
            format="json",
        )
        self.assertEqual(reopened.status_code, 200)

        self.client.force_authenticate(user=self.mixed)
        created = self.client.post(
            "/api/course-entries/",
            {
                "customer_name": "Permitido",
                "people_count": 1,
                "amount_clp": 10000,
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
