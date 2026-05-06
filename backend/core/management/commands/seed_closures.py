from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, CashClosure, calculate_day_totals

class Command(BaseCommand):
    help = "Genera cierres de caja (CashClosure) basados en los datos existentes para los últimos 60 días."

    def handle(self, *args, **kwargs):
        user = User.objects.filter(email="admin@golf.local").first()
        if not user:
            user = User.objects.filter(is_superuser=True).first()
        
        if not user:
            self.stdout.write(self.style.ERROR("No se encontró ningún usuario administrador para asignar los cierres."))
            return

        today = timezone.localtime().date()
        start_date = today - timedelta(days=60)

        closures_created = 0

        self.stdout.write("Generando cierres de caja (Cancha, Range, Final) para los últimos 60 días...")

        for i in range(61):
            current_date = start_date + timedelta(days=i)
            
            # Evitar crear cierres si ya existen
            if CashClosure.objects.filter(operational_date=current_date).exists():
                continue

            totals = calculate_day_totals(current_date)
            
            # Solo crear cierre si hay algún movimiento, o crearlo en 0 si se desea.
            # Lo crearemos siempre para tener el historial continuo.
            
            common_data = {
                "operational_date": current_date,
                "status": CashClosure.STATUS_CLOSED,
                "total_course_clp": totals["total_course_clp"],
                "total_range_clp": totals["total_range_clp"],
                "total_general_clp": totals["total_general_clp"],
                "total_cash_clp": totals["total_cash_clp"],
                "total_card_clp": totals["total_card_clp"],
                "total_transfer_clp": totals["total_transfer_clp"],
                "total_other_clp": totals["total_other_clp"],
                "total_people": totals["total_people"],
                "total_course_records": totals["total_course_records"],
                "total_range_orders": totals["total_range_orders"],
                "total_baskets": totals["total_baskets"],
                "closed_by": user,
            }

            # 1. Cierre Cancha
            CashClosure.objects.create(scope=CashClosure.SCOPE_COURSE, **common_data)
            
            # 2. Cierre Range
            CashClosure.objects.create(scope=CashClosure.SCOPE_RANGE, **common_data)
            
            # 3. Cierre Final
            CashClosure.objects.create(scope=CashClosure.SCOPE_FINAL, **common_data)

            closures_created += 3

        self.stdout.write(self.style.SUCCESS(f"Se crearon exitosamente {closures_created} cierres de caja históricos."))
