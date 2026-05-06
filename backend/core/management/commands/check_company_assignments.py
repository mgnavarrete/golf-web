"""
Comando para verificar que todos los usuarios tengan empresa asignada.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Company, UserCompanyMembership

User = get_user_model()


class Command(BaseCommand):
    help = 'Verifica que todos los usuarios tengan empresa asignada'

    def handle(self, *args, **options):
        self.stdout.write("=== Verificación de Asignación de Empresas ===\n")
        
        # Verificar empresas
        companies = Company.objects.all()
        self.stdout.write(f"Empresas totales: {companies.count()}")
        for company in companies:
            self.stdout.write(f"  - {company.name} (slug: {company.slug}, activa: {company.is_active})")
        
        self.stdout.write("\n=== Usuarios ===\n")
        
        # Verificar usuarios
        users = User.objects.all()
        for user in users:
            self.stdout.write(f"\nUsuario: {user.email}")
            self.stdout.write(f"  - is_superuser: {user.is_superuser}")
            self.stdout.write(f"  - default_company: {user.default_company}")
            
            # Verificar memberships
            memberships = user.company_memberships.filter(is_active=True)
            self.stdout.write(f"  - memberships activas: {memberships.count()}")
            for membership in memberships:
                self.stdout.write(f"    * {membership.company.name} (rol: {membership.role})")
            
            # Determinar empresa activa esperada
            if user.is_superuser:
                # Super admin: primera empresa activa
                first_company = Company.objects.filter(is_active=True).first()
                if first_company:
                    self.stdout.write(f"  ✓ Empresa esperada (super admin): {first_company.name}")
                else:
                    self.stdout.write(self.style.ERROR("  ✗ ERROR: No hay empresas activas"))
            else:
                # Usuario normal
                if user.default_company:
                    self.stdout.write(f"  ✓ Empresa esperada: {user.default_company.name}")
                elif memberships.exists():
                    self.stdout.write(f"  ✓ Empresa esperada (membership): {memberships.first().company.name}")
                else:
                    self.stdout.write(self.style.ERROR("  ✗ ERROR: Usuario sin empresa asignada"))
        
        self.stdout.write("\n=== Resumen ===\n")
        
        # Contar usuarios sin empresa
        users_sin_empresa = []
        for user in users:
            if user.is_superuser:
                if not Company.objects.filter(is_active=True).exists():
                    users_sin_empresa.append(user)
            else:
                if not user.default_company and not user.company_memberships.filter(is_active=True).exists():
                    users_sin_empresa.append(user)
        
        if users_sin_empresa:
            self.stdout.write(self.style.WARNING(f"⚠ {len(users_sin_empresa)} usuarios sin empresa asignada:"))
            for user in users_sin_empresa:
                self.stdout.write(f"  - {user.email}")
        else:
            self.stdout.write(self.style.SUCCESS("✓ Todos los usuarios tienen empresa asignada"))
