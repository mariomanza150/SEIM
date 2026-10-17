from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Role, UserSettings
from accounts.profile_seed import complete_apply_profile
from qa.demo import LEGACY_DEMO_EMAILS, all_demo_specs
from qa.gating import assert_not_production, demo_password

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Create/update one demo account per role (is_demo_account=True, never "
        "superuser) with the shared TESTER_DEMO_PASSWORD, rotate legacy demo "
        "accounts, and optionally mark real users as testers. Refuses to run on "
        "DEPLOY_TIER=production."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--tester",
            action="append",
            default=[],
            metavar="EMAIL",
            help="Mark this existing (non-demo) user as a tester. Repeatable.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        assert_not_production("seed_test_accounts")
        password = demo_password(fallback="demo-dev-password")
        created = updated = 0
        for spec in all_demo_specs():
            role, _ = Role.objects.get_or_create(name=spec["role"])
            user = (
                User.objects.filter(email__iexact=spec["email"]).first()
                or User.objects.filter(username=spec["username"]).first()
            )
            if user is None:
                user = User(username=spec["username"], email=spec["email"])
                created += 1
            else:
                updated += 1
            user.first_name = user.first_name or spec.get("first_name", "")
            user.last_name = user.last_name or spec.get("last_name", "")
            user.is_active = True
            user.is_email_verified = True
            user.is_staff = bool(spec.get("is_staff"))
            user.is_superuser = False
            user.is_demo_account = True
            user.is_tester = False
            user.set_password(password)
            user.save()
            user.roles.set([role])
            UserSettings.objects.get_or_create(user=user)
            if spec["role"] == "student":
                complete_apply_profile(user)

        rotated = 0
        for user in User.objects.filter(email__in=LEGACY_DEMO_EMAILS):
            user.is_superuser = False
            user.is_demo_account = True
            user.is_tester = False
            user.set_password(password)
            user.save()
            rotated += 1

        for email in options["tester"]:
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                self.stdout.write(
                    self.style.WARNING(f"  No user with email {email}; skipped.")
                )
                continue
            if user.is_demo_account:
                raise CommandError(f"{email} is a demo account and cannot be a tester.")
            if not user.is_tester:
                user.is_tester = True
                user.save(update_fields=["is_tester"])
            self.stdout.write(self.style.SUCCESS(f"  Marked {email} as tester."))

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo accounts: {created} created, {updated} updated, "
                f"{rotated} legacy rotated. Password: TESTER_DEMO_PASSWORD (not shown)."
            )
        )
