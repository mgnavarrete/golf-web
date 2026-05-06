"""Legacy tests removed: app now runs in single-company mode."""

from django.test import TestCase


class SingleCompanyPlaceholderTests(TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
