from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def seed_business_settings(sender, **kwargs):
    if sender.name != "core":
        return

    from .models import BusinessSettings, User

    BusinessSettings.get_solo()

    # Mantener compatibilidad para usuarios preexistentes
    User.objects.filter(role="").update(role=User.ROLE_MIXED)
