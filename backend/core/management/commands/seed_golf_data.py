import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, CourseEntry, RangeOrder, PaymentMethod, BusinessSettings

class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba para los últimos 60 días."

    def handle(self, *args, **kwargs):
        self.stdout.write("Buscando o creando usuario administrador por defecto...")
        user, created = User.objects.get_or_create(
            email="admin@golf.local",
            defaults={"is_staff": True, "is_superuser": True, "role": User.ROLE_ADMIN}
        )
        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Usuario {user.email} creado con clave admin123."))

        settings = BusinessSettings.get_solo()
        default_range_price = settings.default_range_unit_price_clp

        names = ["Juan Pérez", "María Gómez", "Carlos Silva", "Ana Rojas", "Luis Torres", 
                 "Sofía Vargas", "Diego Morales", "Camila Castro", "Jorge Ortiz", "Valentina Ríos",
                 "Socio Anónimo", "Invitado Club"]

        payment_methods = [PaymentMethod.CASH, PaymentMethod.CARD, PaymentMethod.TRANSFER, PaymentMethod.OTHER]
        
        # Probabilidades de pago: 50% Tarjeta, 30% Transferencia, 15% Efectivo, 5% Otro
        payment_weights = [15, 50, 30, 5]

        today = timezone.now()
        start_date = today - timedelta(days=60)

        course_entries_created = 0
        range_orders_created = 0

        self.stdout.write("Generando datos para los últimos 60 días...")

        for i in range(61):
            current_date = start_date + timedelta(days=i)
            # Fin de semana: más gente
            is_weekend = current_date.weekday() >= 5
            
            num_course = random.randint(5, 25) if is_weekend else random.randint(1, 10)
            num_range = random.randint(10, 40) if is_weekend else random.randint(2, 15)

            # --- Generar Course Entries ---
            for _ in range(num_course):
                people = random.randint(1, 4)
                # Precio depende si es fin de semana o no (simplificado para el script)
                price_per_person = 25000 if is_weekend else 20000
                amount = people * price_per_person
                method = random.choices(payment_methods, weights=payment_weights)[0]

                # Tiempo aleatorio dentro del día (entre 8:00 y 18:00)
                random_hour = random.randint(8, 18)
                random_minute = random.randint(0, 59)
                entry_date = current_date.replace(hour=random_hour, minute=random_minute)

                entry = CourseEntry(
                    customer_name=random.choice(names),
                    people_count=people,
                    amount_clp=amount,
                    payment_method=method,
                    created_by=user
                )
                entry.save()
                # Truco para sobreescribir auto_now_add
                CourseEntry.objects.filter(pk=entry.pk).update(created_at=entry_date)
                course_entries_created += 1

            # --- Generar Range Orders ---
            for _ in range(num_range):
                baskets = random.randint(1, 10)
                method = random.choices(payment_methods, weights=payment_weights)[0]

                random_hour = random.randint(8, 20)
                random_minute = random.randint(0, 59)
                order_date = current_date.replace(hour=random_hour, minute=random_minute)

                order = RangeOrder(
                    customer_name=random.choice(names),
                    baskets_count=baskets,
                    unit_price_clp=default_range_price,
                    payment_method=method,
                    created_by=user
                )
                order.save()
                RangeOrder.objects.filter(pk=order.pk).update(created_at=order_date)
                range_orders_created += 1

        self.stdout.write(self.style.SUCCESS(f"Se crearon exitosamente {course_entries_created} entradas a cancha y {range_orders_created} pedidos de driving range."))
