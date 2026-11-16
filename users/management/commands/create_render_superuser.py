import os
import re

from django.core.management.base import BaseCommand, CommandError

from users.models import CustomUser


class Command(BaseCommand):
    help = "Creates the Render superuser using environment-provided credentials"

    def handle(self, *args, **options):
        if CustomUser.objects.filter(username="admin").exists():
            self.stdout.write(self.style.WARNING("Superuser already exists."))
            return

        phone_number = os.environ.get("RENDER_ADMIN_PHONE")
        pin = os.environ.get("RENDER_ADMIN_PIN")
        if not phone_number or not re.fullmatch(r"\d{4}", pin or ""):
            raise CommandError(
                "Set RENDER_ADMIN_PHONE and a 4-digit RENDER_ADMIN_PIN."
            )

        CustomUser.objects.create_superuser(
            username="admin",
            phone_number=phone_number,
            password=pin,
        )
        self.stdout.write(self.style.SUCCESS("Superuser created."))