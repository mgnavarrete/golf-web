"""
Comando para asignar empresa por defecto a usuarios que no la tengan.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Company, UserCompanyMembership

User = get_user_model()


class Command(BaseCommand):
    help = 'Asigna empresa Minttu SpA a usuarios que no tengan empresa asignada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Obtener empresa Minttu SpA
        minttu = Company.objects.filter(slug='minttu').first()
        if not minttu:
            self.stdout.write(self.style.ERROR("ERROR: No existe empresa con slug 'minttu'"))
            self.stdout.write("Ejecuta primero las migraciones para crear la empresa.")
            return
        
        self.stdout.write(f"Empresa objetivo: {minttu.name} (ID: {minttu.id})\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: No se harán cambios\n"))
        
        # Procesar usuarios normales (no superusers)
        normal_users = User.objects.filter(is_superuser=False)
        updated_count = 0
        
        for user in normal_users:
            needs_update = False
            
            # Verificar si necesita default_company
            if not user.default_company:
                self.stdout.write(f"Usuario {user.email}: sin default_company")
                needs_update = True
            
            # Verificar si necesita membership
            has_active_membership = user.company_memberships.filter(
                is_active=True,
                company=minttu
            ).exists()
            
            if not has_active_membership:
                if needs_update:
                    self.stdout.write(f"  - También sin membership activa")
                else:
                    self.stdout.write(f"Usuario {user.email}: sin membership activa")
                needs_update = True
            
            if needs_update:
                if not dry_run:
                    # Asignar default_company
                    if not user.default_company:
                        user.default_company = minttu
                        user.save(update_fields=['default_company'])
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Asignado default_company"))
                    
                    # Crear membership si no existe
                    if not has_active_membership:
                        UserCompanyMembership.objects.get_or_create(
                            user=user,
                            company=minttu,
                            defaults={
                                'role': UserCompanyMembership.ROLE_MEMBER,
                                'is_active': True
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Creada membership"))
                
                updated_count += 1
        
        # Procesar superusers (no necesitan default_company, pero verificar que hay empresas)
        superusers = User.objects.filter(is_superuser=True)
        self.stdout.write(f"\nSuper admins: {superusers.count()}")
        for user in superusers:
            self.stdout.write(f"  - {user.email} (no necesita default_company)")
        
        self.stdout.write(f"\n=== Resumen ===")
        if dry_run:
            self.stdout.write(self.style.WARNING(f"Se actualizarían {updated_count} usuarios"))
            self.stdout.write("Ejecuta sin --dry-run para aplicar los cambios")
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ {updated_count} usuarios actualizados"))
