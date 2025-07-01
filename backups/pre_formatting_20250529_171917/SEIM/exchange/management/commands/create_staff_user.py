"""
Management command to create staff users with specific roles.
"""

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token

from exchange.models import Exchange, UserProfile


class Command(BaseCommand):
    help = "Create a staff user with a specific role"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username for the new user")
        parser.add_argument("email", type=str, help="Email address for the new user")
        parser.add_argument(
            "--role",
            type=str,
            default="COORDINATOR",
            choices=["COORDINATOR", "MANAGER", "ADMIN"],
            help="Role for the user (default: COORDINATOR)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Password for the user (if not provided, will be prompted)",
        )
        parser.add_argument(
            "--first-name", type=str, default="", help="First name of the user"
        )
        parser.add_argument(
            "--last-name", type=str, default="", help="Last name of the user"
        )
        parser.add_argument(
            "--institution", type=str, default="", help="Institution for the user"
        )
        parser.add_argument(
            "--department", type=str, default="", help="Department for the user"
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        role = options["role"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]
        institution = options["institution"]
        department = options["department"]

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists')

        # Get password if not provided
        if not password:
            password = self.get_password()

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Set staff status based on role
        user.is_staff = True
        if role == "ADMIN":
            user.is_superuser = True
        user.save()

        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            role=role,
            institution=institution,
            department=department,
            is_verified=True,
        )

        # Create auth token
        token, created = Token.objects.get_or_create(user=user)

        # Assign permissions based on role
        self.assign_permissions(user, role)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {role} user "{username}" with token: {token.key}'
            )
        )

        # Display user details
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Role: {role}")
        self.stdout.write(f"Institution: {institution}")
        self.stdout.write(f"Department: {department}")

        # Display assigned permissions
        self.stdout.write("\nAssigned permissions:")
        for perm in user.user_permissions.all():
            self.stdout.write(f"  - {perm.name}")

    def get_password(self):
        """Prompt for password"""
        import getpass

        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            raise CommandError("Passwords do not match")

        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters long")

        return password

    def assign_permissions(self, user, role):
        """Assign permissions based on role"""
        exchange_content_type = ContentType.objects.get_for_model(Exchange)

        # Get permissions
        can_view_all = Permission.objects.get(
            codename="can_view_all_exchanges", content_type=exchange_content_type
        )
        can_approve = Permission.objects.get(
            codename="can_approve_exchange", content_type=exchange_content_type
        )
        can_reject = Permission.objects.get(
            codename="can_reject_exchange", content_type=exchange_content_type
        )

        # Assign permissions based on role
        if role == "COORDINATOR":
            # Coordinators can view all exchanges
            user.user_permissions.add(can_view_all)

        elif role == "MANAGER":
            # Managers can view all, approve, and reject
            user.user_permissions.add(can_view_all, can_approve, can_reject)

        elif role == "ADMIN":
            # Admins get all permissions through is_superuser
            pass
