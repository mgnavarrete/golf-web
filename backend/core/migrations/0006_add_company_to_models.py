# Generated migration for adding company relationships to User, Camera, and Report

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_minttu_company_and_backfill(apps, schema_editor):
    """
    Crea la empresa 'Minttu SpA' y asigna todas las cámaras y reportes existentes.
    IDEMPOTENTE: Puede ejecutarse múltiples veces sin problemas.
    NO TOCA USUARIOS NI MEMBERSHIPS.
    """
    Company = apps.get_model('core', 'Company')
    Camera = apps.get_model('core', 'Camera')
    Report = apps.get_model('core', 'Report')
    
    # Crear empresa Minttu SpA si no existe (idempotente)
    minttu_company, created = Company.objects.get_or_create(
        slug='minttu',
        defaults={
            'name': 'Minttu SpA',
            'is_active': True
        }
    )
    
    # Si ya existía pero tenía otro nombre, actualizar nombre
    if not created and minttu_company.name != 'Minttu SpA':
        minttu_company.name = 'Minttu SpA'
        minttu_company.is_active = True
        minttu_company.save(update_fields=['name', 'is_active'])
    
    # Backfill de cámaras: asignar todas las que no tienen company
    cameras_updated = Camera.objects.filter(company__isnull=True).update(company=minttu_company)
    print(f"✓ {cameras_updated} cámaras asignadas a Minttu SpA")
    
    # Backfill de reportes: asignar todos los que no tienen company
    reports_updated = Report.objects.filter(company__isnull=True).update(company=minttu_company)
    print(f"✓ {reports_updated} reportes asignados a Minttu SpA")
    
    # Verificar que no quedan cámaras sin company
    cameras_sin_company = Camera.objects.filter(company__isnull=True).count()
    if cameras_sin_company > 0:
        raise ValueError(f"ERROR: Quedan {cameras_sin_company} cámaras sin company asignada")
    
    # Verificar que no quedan reportes sin company
    reports_sin_company = Report.objects.filter(company__isnull=True).count()
    if reports_sin_company > 0:
        raise ValueError(f"ERROR: Quedan {reports_sin_company} reportes sin company asignada")


def reverse_migration(apps, schema_editor):
    """No hay reversión segura - los datos ya estarían asociados"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_create_company_and_membership'),
    ]

    operations = [
        # Agregar default_company a User (nullable)
        migrations.AddField(
            model_name='user',
            name='default_company',
            field=models.ForeignKey(
                blank=True,
                help_text='Empresa por defecto del usuario (para usuarios normales)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='default_users',
                to='core.company'
            ),
        ),
        # Agregar company a Camera (nullable primero, luego NOT NULL después del backfill)
        migrations.AddField(
            model_name='camera',
            name='company',
            field=models.ForeignKey(
                help_text='Empresa a la que pertenece esta cámara',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='cameras',
                to='core.company'
            ),
        ),
        # Agregar company a Report (nullable primero, luego NOT NULL después del backfill)
        migrations.AddField(
            model_name='report',
            name='company',
            field=models.ForeignKey(
                help_text='Empresa a la que pertenece este reporte',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reports',
                to='core.company'
            ),
        ),
        # Ejecutar backfill de datos
        migrations.RunPython(create_minttu_company_and_backfill, reverse_migration),
        # Hacer company NOT NULL en Camera (después del backfill)
        migrations.AlterField(
            model_name='camera',
            name='company',
            field=models.ForeignKey(
                help_text='Empresa a la que pertenece esta cámara',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='cameras',
                to='core.company'
            ),
        ),
        # Hacer company NOT NULL en Report (después del backfill)
        migrations.AlterField(
            model_name='report',
            name='company',
            field=models.ForeignKey(
                help_text='Empresa a la que pertenece este reporte',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='reports',
                to='core.company'
            ),
        ),
        # Crear índices para performance
        migrations.AddIndex(
            model_name='camera',
            index=models.Index(fields=['company'], name='camera_company_idx'),
        ),
        migrations.AddIndex(
            model_name='camera',
            index=models.Index(fields=['company', 'is_active'], name='camera_company_active_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['company'], name='report_company_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['company', 'created_at'], name='report_company_created_idx'),
        ),
    ]
