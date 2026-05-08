from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import UserProfile


class Command(BaseCommand):
    help = "Ensures all superusers have admin_pro role in their profile"

    def handle(self, *args, **kwargs):
        superusers = User.objects.filter(is_superuser=True)
        if not superusers.exists():
            self.stdout.write(self.style.WARNING("No superusers found."))
            return

        for user in superusers:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'rol': 'admin_pro'}
            )
            if not created and profile.rol != 'admin_pro':
                profile.rol = 'admin_pro'
                profile.save(update_fields=['rol'])
                self.stdout.write(self.style.SUCCESS(
                    f"Updated '{user.username}' profile to admin_pro"
                ))
            elif created:
                self.stdout.write(self.style.SUCCESS(
                    f"Created admin_pro profile for '{user.username}'"
                ))
            else:
                self.stdout.write(f"'{user.username}' already has admin_pro role")
