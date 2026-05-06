"""
Script para corregir permisos de usuarios admin
Ejecutar con: python manage.py shell < fix_admin_permissions.py
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

print("=" * 60)
print("CORRIGIENDO PERMISOS DE USUARIOS")
print("=" * 60)

# Obtener o crear grupos
superadmin_group, _ = Group.objects.get_or_create(name="SuperAdmin")
admin_group, _ = Group.objects.get_or_create(name="Admin")
viewer_group, _ = Group.objects.get_or_create(name="Viewer")

print("\n✓ Grupos verificados:")
print(f"  • SuperAdmin (ID: {superadmin_group.id})")
print(f"  • Admin (ID: {admin_group.id})")
print(f"  • Viewer (ID: {viewer_group.id})")

# Obtener todos los usuarios
users = User.objects.all()

print("\n" + "=" * 60)
print("PROCESANDO USUARIOS")
print("=" * 60)

for user in users:
    print(f"\n📧 {user.email}")
    
    # Determinar rol basado en grupos
    user_groups = list(user.groups.values_list('name', flat=True))
    print(f"   Grupos actuales: {', '.join(user_groups) if user_groups else 'Ninguno'}")
    
    # Verificar y corregir según los grupos
    needs_update = False
    
    if "SuperAdmin" in user_groups:
        # Super Admin debe tener is_staff=True, is_superuser=True
        if not user.is_staff or not user.is_superuser:
            print(f"   ⚠️  Corrigiendo: Super Admin sin permisos completos")
            user.is_staff = True
            user.is_superuser = True
            needs_update = True
    
    elif "Admin" in user_groups:
        # Admin debe tener is_staff=True, is_superuser=False
        if not user.is_staff or user.is_superuser:
            print(f"   ⚠️  Corrigiendo: Admin con permisos incorrectos")
            user.is_staff = True
            user.is_superuser = False
            needs_update = True
    
    elif "Viewer" in user_groups:
        # Viewer debe tener is_staff=False, is_superuser=False
        if user.is_staff or user.is_superuser:
            print(f"   ⚠️  Corrigiendo: Viewer con permisos elevados")
            user.is_staff = False
            user.is_superuser = False
            needs_update = True
    
    else:
        # Usuario sin grupo definido - asignar según permisos actuales
        if user.is_superuser:
            print(f"   ⚠️  Sin grupo, asignando: SuperAdmin")
            user.groups.clear()
            user.groups.add(superadmin_group)
            user.is_staff = True
            user.is_superuser = True
            needs_update = True
        elif user.is_staff:
            print(f"   ⚠️  Sin grupo, asignando: Admin")
            user.groups.clear()
            user.groups.add(admin_group)
            user.is_staff = True
            user.is_superuser = False
            needs_update = True
        else:
            print(f"   ⚠️  Sin grupo, asignando: Viewer")
            user.groups.clear()
            user.groups.add(viewer_group)
            user.is_staff = False
            user.is_superuser = False
            needs_update = True
    
    if needs_update:
        user.save()
        print(f"   ✅ Usuario actualizado")
        print(f"      is_staff: {user.is_staff}")
        print(f"      is_superuser: {user.is_superuser}")
        print(f"      Grupos: {', '.join(user.groups.values_list('name', flat=True))}")
    else:
        print(f"   ✓ Permisos correctos")

print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)

superadmins = User.objects.filter(is_superuser=True)
admins = User.objects.filter(is_staff=True, is_superuser=False)
viewers = User.objects.filter(is_staff=False, is_superuser=False)

print(f"\n👑 Super Admins ({superadmins.count()}):")
for user in superadmins:
    print(f"   • {user.email}")

print(f"\n⚙️  Admins ({admins.count()}):")
for user in admins:
    print(f"   • {user.email}")

print(f"\n👁️  Viewers ({viewers.count()}):")
for user in viewers:
    print(f"   • {user.email}")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
