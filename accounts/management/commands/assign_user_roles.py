from django.core.management.base import BaseCommand

from accounts.models import Role, User


class Command(BaseCommand):
    help = "Assign roles to existing users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Username to assign role to (optional)",
        )
        parser.add_argument(
            "--role",
            type=str,
            choices=["admin", "coordinator", "student"],
            help="Role to assign (optional)",
        )

    def handle(self, *args, **options):
        username = options.get("username")
        role_name = options.get("role")

        # Create roles if they don't exist
        roles = {}
        for role_type in ["admin", "coordinator", "student"]:
            role, created = Role.objects.get_or_create(name=role_type)
            roles[role_type] = role
            if created:
                self.stdout.write(f"Created role: {role_type}")

        if username and role_name:
            # Assign specific role to specific user
            try:
                user = User.objects.get(username=username)
                role = roles[role_name]
                user.roles.add(role)
                self.stdout.write(f"Assigned {role_name} role to user {username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {username} not found"))
        else:
            # Default role assignment logic
            self.stdout.write("Assigning default roles to users...")

            # Assign admin role to superusers
            admin_role = roles["admin"]
            admin_users = User.objects.filter(is_superuser=True)
            for user in admin_users:
                user.roles.add(admin_role)
                self.stdout.write(f"Assigned admin role to superuser: {user.username}")

            # Assign coordinator role to staff users (but not superusers)
            coordinator_role = roles["coordinator"]
            staff_users = User.objects.filter(is_staff=True, is_superuser=False)
            for user in staff_users:
                user.roles.add(coordinator_role)
                self.stdout.write(
                    f"Assigned coordinator role to staff user: {user.username}"
                )

            # Assign student role to regular users
            student_role = roles["student"]
            regular_users = User.objects.filter(is_staff=False, is_superuser=False)
            for user in regular_users:
                user.roles.add(student_role)
                self.stdout.write(
                    f"Assigned student role to regular user: {user.username}"
                )

        self.stdout.write(self.style.SUCCESS("Role assignment completed!"))
