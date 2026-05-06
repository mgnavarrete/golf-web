from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, CashClosure, calculate_scope_totals, combine_closure_totals

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

            course_totals = calculate_scope_totals(current_date, CashClosure.SCOPE_COURSE)
            range_totals = calculate_scope_totals(current_date, CashClosure.SCOPE_RANGE)
            
            # Solo crear cierre si hay algún movimiento, o crearlo en 0 si se desea.
            # Lo crearemos siempre para tener el historial continuo.
            
            common_data = {
                "operational_date": current_date,
                "status": CashClosure.STATUS_CLOSED,
                "closed_by": user,
            }

            # 1. Cierre Cancha
            course_closure = CashClosure.objects.create(scope=CashClosure.SCOPE_COURSE, **common_data, **course_totals)
            
            # 2. Cierre Range
            range_closure = CashClosure.objects.create(scope=CashClosure.SCOPE_RANGE, **common_data, **range_totals)
            
            # 3. Cierre Final
            final_totals = combine_closure_totals(course_closure, range_closure)
            CashClosure.objects.create(scope=CashClosure.SCOPE_FINAL, **common_data, **final_totals)

            closures_created += 3

        self.stdout.write(self.style.SUCCESS(f"Se crearon exitosamente {closures_created} cierres de caja históricos."))
