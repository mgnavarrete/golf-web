"""
Script para actualizar el equipo Edge existente con empresa y ubicación
Ejecutar con: python manage.py shell < update_edge_device.py
"""
from core.models import EdgeDevice, Company, Camera

print("=" * 60)
print("ACTUALIZANDO EQUIPO EDGE")
print("=" * 60)

# Obtener la empresa
company = Company.objects.first()
if not company:
    print("⚠️  No hay empresas en la base de datos")
    exit()

print(f"\n✓ Empresa encontrada: {company.name} (ID: {company.id})")

# Obtener el equipo Edge
edge = EdgeDevice.objects.first()
if not edge:
    print("⚠️  No hay equipos Edge en la base de datos")
    exit()

print(f"✓ Equipo Edge encontrado: {edge.name}")

# Obtener cámara para copiar coordenadas
camera = Camera.objects.filter(latitude__isnull=False, longitude__isnull=False).first()
if camera:
    print(f"✓ Cámara encontrada para copiar coordenadas: {camera.name}")
    print(f"  Ubicación: {camera.location_name}")
    print(f"  Coordenadas: {camera.latitude}, {camera.longitude}")
    
    # Actualizar equipo Edge
    edge.company = company
    edge.location_name = "Oficina TI"
    edge.latitude = camera.latitude
    edge.longitude = camera.longitude
    edge.save()
    
    print(f"\n✓ Equipo Edge actualizado:")
    print(f"  - Empresa: {edge.company.name}")
    print(f"  - Ubicación: {edge.location_name}")
    print(f"  - Coordenadas: {edge.latitude}, {edge.longitude}")
else:
    # Solo asignar empresa
    edge.company = company
    edge.location_name = "Oficina TI"
    edge.save()
    
    print(f"\n✓ Equipo Edge actualizado:")
    print(f"  - Empresa: {edge.company.name}")
    print(f"  - Ubicación: {edge.location_name}")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
