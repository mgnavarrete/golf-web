# Generated manually

from django.db import migrations, models
import random


def assign_random_icons(apps, schema_editor):
    """Asignar iconos aleatorios a usuarios existentes"""
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        if not user.profile_icon or user.profile_icon < 1 or user.profile_icon > 10:
            user.profile_icon = random.randint(1, 10)
            user.save(update_fields=['profile_icon'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_edgedevice_edge_device_is_acti_66b9aa_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_icon',
            field=models.IntegerField(default=1, help_text='Icono de perfil (1-10)'),
        ),
        migrations.RunPython(assign_random_icons, migrations.RunPython.noop),
    ]

