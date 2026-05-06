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
