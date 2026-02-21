import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create/update an admin user from env vars (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_ADMIN_USERNAME", "").strip()
        email = os.getenv("DJANGO_ADMIN_EMAIL", "").strip()
        password = os.getenv("DJANGO_ADMIN_PASSWORD", "").strip()

        if not username or not password:
            self.stdout.write(self.style.WARNING("DJANGO_ADMIN_USERNAME/PASSWORD not set. Skipping ensure_admin."))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        changed = False

        # garantir email
        if email and user.email != email:
            user.email = email
            changed = True

        # garantir superuser + staff
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        # garantir password (sempre set para ficar simples)
        user.set_password(password)
        changed = True

        if changed:
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Admin created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS("Admin ensured/updated successfully."))