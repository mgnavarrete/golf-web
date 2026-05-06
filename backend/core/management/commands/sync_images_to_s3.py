import os
from django.core.management.base import BaseCommand
from django.conf import settings

from core.models import AlertEvent
from core.services.s3 import upload_bytes_to_s3


class Command(BaseCommand):
    help = "Sube a S3 las imágenes de AlertEvent usando snapshot_url como key, buscando los archivos en una carpeta local."

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            required=True,
            help="Carpeta donde están las imágenes locales (ej: /mnt/e/.../alerts_old)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Cantidad máxima a subir (0 = sin límite)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No sube, solo muestra qué haría",
        )

    def handle(self, *args, **opts):
        folder = opts["folder"]
        limit = opts["limit"]
        dry_run = opts["dry_run"]

        if not os.path.isdir(folder):
            self.stderr.write(self.style.ERROR(f"No existe carpeta: {folder}"))
            return

        # index local files by filename
        local_files = {}
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                local_files[name] = path

        qs = AlertEvent.objects.exclude(snapshot_url__isnull=True).exclude(snapshot_url="").order_by("id")
        if limit and limit > 0:
            qs = qs[:limit]

        uploaded = 0
        missing = 0

        for alert in qs:
            key = alert.snapshot_url  # ej: CAM_01/CELLPHONE/xxx.jpg
            filename = key.split("/")[-1]

            local_path = local_files.get(filename)
            if not local_path:
                missing += 1
                self.stdout.write(self.style.WARNING(f"[MISS] id={alert.id} no encuentro archivo local: {filename} (key={key})"))
                continue

            self.stdout.write(f"[UPLOAD] id={alert.id} {local_path} -> s3://{settings.AWS_STORAGE_BUCKET_NAME}/{key}")

            if not dry_run:
                with open(local_path, "rb") as f:
                    content_type = "image/jpeg"
                    if filename.lower().endswith(".png"):
                        content_type = "image/png"
                    upload_bytes_to_s3(f.read(), key, content_type=content_type)

            uploaded += 1

        self.stdout.write(self.style.SUCCESS(f"Listo. Subidos: {uploaded} | Faltantes: {missing}"))
