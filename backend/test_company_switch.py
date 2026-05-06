"""
Script para probar el cambio de empresa
Ejecutar con: python manage.py shell < test_company_switch.py
"""
from core.models import Company, AlertEvent, Camera
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("VERIFICANDO EMPRESAS Y DATOS")
print("=" * 60)

# Listar empresas
print("\n📋 EMPRESAS DISPONIBLES:")
print("-" * 60)
companies = Company.objects.all()
for company in companies:
    print(f"\n🏢 {company.name}")
    print(f"   ID: {company.id}")
    print(f"   Slug: {company.slug}")
    print(f"   Activa: {'✅ Sí' if company.is_active else '❌ No'}")
    
    # Contar alertas
    alert_count = AlertEvent.objects.filter(camera__company=company).count()
    print(f"   Alertas: {alert_count}")
    
    # Contar cámaras
    camera_count = Camera.objects.filter(company=company).count()
    print(f"   Cámaras: {camera_count}")

# Verificar super admin
print("\n" + "=" * 60)
print("VERIFICANDO SUPER ADMIN")
print("=" * 60)

superadmins = User.objects.filter(is_superuser=True)
print(f"\nSuper Admins encontrados: {superadmins.count()}")

for user in superadmins:
    print(f"\n👑 {user.email}")
    print(f"   ID: {user.id}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_active: {user.is_active}")
    if user.default_company:
        print(f"   Empresa por defecto: {user.default_company.name}")

print("\n" + "=" * 60)
print("SIMULACIÓN DE CAMBIO DE EMPRESA")
print("=" * 60)

if companies.count() >= 2:
    company1 = companies[0]
    company2 = companies[1]
    
    print(f"\n1️⃣ Empresa 1: {company1.name} (ID: {company1.id})")
    alerts1 = AlertEvent.objects.filter(camera__company=company1).count()
    print(f"   Alertas: {alerts1}")
    
    print(f"\n2️⃣ Empresa 2: {company2.name} (ID: {company2.id})")
    alerts2 = AlertEvent.objects.filter(camera__company=company2).count()
    print(f"   Alertas: {alerts2}")
    
    if alerts1 > 0 and alerts2 == 0:
        print("\n⚠️  IMPORTANTE:")
        print(f"   {company2.name} NO tiene alertas.")
        print(f"   Si cambias a {company2.name}, NO verás ninguna alerta.")
        print(f"   Esto es CORRECTO - es el comportamiento esperado.")
    elif alerts1 > 0 and alerts2 > 0:
        print("\n✅ PERFECTO:")
        print(f"   Ambas empresas tienen alertas.")
        print(f"   Al cambiar entre ellas, deberías ver datos diferentes.")
    else:
        print("\n⚠️  NOTA:")
        print(f"   Verifica que haya datos en ambas empresas para probar el cambio.")
else:
    print("\n⚠️  Solo hay una empresa en la base de datos.")
    print("   No se puede probar el cambio de empresa.")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
