from django.core.management.base import BaseCommand
from core.models import EdgeDevice


class Command(BaseCommand):
    help = "Crea un EdgeDevice y genera un API key (se muestra una sola vez)."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)

    def handle(self, *args, **opts):
        name = opts["name"]
        raw = EdgeDevice.generate_key()
        hashed = EdgeDevice.hash_key(raw)

        dev = EdgeDevice.objects.create(name=name, api_key_hash=hashed)
        self.stdout.write(self.style.SUCCESS(f"EdgeDevice creado id={dev.id} name={dev.name}"))
        self.stdout.write(self.style.WARNING("API KEY (guárdala, no se puede recuperar):"))
        self.stdout.write(raw)
