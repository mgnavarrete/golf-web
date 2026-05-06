"""
Script para verificar los permisos de los usuarios admin
Ejecutar con: python manage.py shell < check_admin_users.py
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

print("=" * 60)
print("VERIFICANDO USUARIOS Y PERMISOS")
print("=" * 60)

users = User.objects.all()

for user in users:
    print(f"\n📧 Email: {user.email}")
    print(f"   Nombre: {user.first_name} {user.last_name}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_active: {user.is_active}")
    
    groups = user.groups.all()
    if groups:
        print(f"   Grupos: {', '.join([g.name for g in groups])}")
    else:
        print(f"   Grupos: Ninguno")
    
    # Determinar rol esperado
    if user.is_superuser:
        expected_role = "Super Admin"
    elif user.is_staff:
        expected_role = "Admin"
    else:
        expected_role = "Viewer"
    
    print(f"   Rol esperado: {expected_role}")
    
    # Verificar si debería ver Configuración
    can_access_config = user.is_staff or user.is_superuser
    print(f"   Puede acceder a Configuración: {'✅ SÍ' if can_access_config else '❌ NO'}")

print("\n" + "=" * 60)
print("GRUPOS DISPONIBLES")
print("=" * 60)

groups = Group.objects.all()
for group in groups:
    print(f"• {group.name}")
    users_in_group = group.user_set.all()
    if users_in_group:
        for user in users_in_group:
            print(f"  - {user.email}")
    else:
        print(f"  (sin usuarios)")

print("\n" + "=" * 60)
