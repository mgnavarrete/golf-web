# Generated migration for multi-tenant support

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.text


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_comments_and_last_modified_to_alerts'),
    ]

    operations = [
        # Crear modelo Company
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nombre de la empresa', max_length=200, unique=True)),
                ('slug', models.SlugField(help_text='Slug único para URLs', max_length=200, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Indica si la empresa está activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresas',
                'db_table': 'company',
            },
        ),
        # Crear índices para Company
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['slug'], name='company_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['is_active'], name='company_is_active_idx'),
        ),
        # Crear modelo UserCompanyMembership
        migrations.CreateModel(
            name='UserCompanyMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ADMIN', 'Administrador'), ('MEMBER', 'Miembro'), ('VIEWER', 'Visualizador')], default='MEMBER', help_text='Rol del usuario en esta empresa', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Indica si la membresía está activa')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='core.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Membresía de Usuario',
                'verbose_name_plural': 'Membresías de Usuarios',
                'db_table': 'user_company_membership',
                'unique_together': {('user', 'company')},
            },
        ),
        # Crear índices para UserCompanyMembership
        migrations.AddIndex(
            model_name='usercompanymembership',
            index=models.Index(fields=['user', 'company'], name='membership_user_company_idx'),
        ),
        migrations.AddIndex(
            model_name='usercompanymembership',
            index=models.Index(fields=['user', 'is_active'], name='membership_user_active_idx'),
        ),
        migrations.AddIndex(
            model_name='usercompanymembership',
            index=models.Index(fields=['company', 'is_active'], name='membership_company_active_idx'),
        ),
    ]
