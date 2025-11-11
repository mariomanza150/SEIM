from django.core.management.base import BaseCommand

from accounts.models import Profile, User


class Command(BaseCommand):
    help = "Create profiles for users that do not have them"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find users without profiles
        users_without_profiles = []
        for user in User.objects.all():
            try:
                user.profile
            except User.profile.RelatedObjectDoesNotExist:
                users_without_profiles.append(user)

        if not users_without_profiles:
            self.stdout.write(self.style.SUCCESS("All users already have profiles!"))
            return

        self.stdout.write(
            f"Found {len(users_without_profiles)} users without profiles:"
        )
        for user in users_without_profiles:
            self.stdout.write(f"  - {user.username} ({user.email})")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN: Would create profiles for the above users")
            )
            return

        # Create profiles
        created_count = 0
        for user in users_without_profiles:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(f"Created profile for {user.username}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} profiles")
        )
