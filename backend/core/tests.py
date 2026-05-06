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
