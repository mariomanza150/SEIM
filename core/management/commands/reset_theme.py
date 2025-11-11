
from django.contrib.auth import get_user_model

User = get_user_model()
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset theme preferences for all users or specific user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="Reset theme for specific user (username)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Reset theme for all users",
        )
        parser.add_argument(
            "--force-light",
            action="store_true",
            help="Force light mode for all users",
        )
        parser.add_argument(
            "--force-dark",
            action="store_true",
            help="Force dark mode for all users",
        )

    def handle(self, *args, **options):
        if options["user"]:
            self.reset_user_theme(options["user"], options)
        elif options["all"]:
            self.reset_all_users_theme(options)
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Please specify --user <username> or --all to reset themes"
                )
            )

    def reset_user_theme(self, username, options):
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Resetting theme for user: {username}")

            # Clear any cached theme preferences
            cache_key = f"user_theme_{user.id}"
            cache.delete(cache_key)

            # Set default theme preference
            if options["force_light"]:
                theme = "light"
            elif options["force_dark"]:
                theme = "dark"
            else:
                theme = "system"  # Default to system preference

            # Store in user profile or preferences
            self.set_user_theme_preference(user, theme)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Theme reset for user {username} to {theme}"
                )
            )

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User not found"))

    def reset_all_users_theme(self, options):
        users = User.objects.all()
        self.stdout.write(f"Resetting theme for {users.count()} users...")

        theme = "system"  # Default
        if options["force_light"]:
            theme = "light"
        elif options["force_dark"]:
            theme = "dark"

        for user in users:
            # Clear cached preferences
            cache_key = f"user_theme_{user.id}"
            cache.delete(cache_key)

            # Set theme preference
            self.set_user_theme_preference(user, theme)

        self.stdout.write(
            self.style.SUCCESS(
                f"Theme reset for {users.count()} users to {theme}"
            )
        )

    def set_user_theme_preference(self, user, theme):
        """
        Set theme preference for a user
        This can be extended to store in user profile or preferences model
        """
        # For now, we'll store in cache
        cache_key = f"user_theme_{user.id}"
        cache.set(cache_key, theme, timeout=86400)  # 24 hours

        # If you have a user preferences model, you can store it there
        # Example:
        # UserPreference.objects.update_or_create(
        #     user=user,
        #     key='theme',
        #     defaults={'value': theme}
        # )

        self.stdout.write(f"  - User {user.username}: {theme}")
