"""
Management command to set up Wagtail permissions for existing staff users.

This command ensures that all staff users have the necessary permissions
to access and use the Wagtail admin interface.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Collection


User = get_user_model()


class Command(BaseCommand):
    help = 'Set up Wagtail permissions for existing staff users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-editors-group',
            action='store_true',
            help='Create an Editors group with appropriate permissions',
        )
        parser.add_argument(
            '--create-moderators-group',
            action='store_true',
            help='Create a Moderators group with appropriate permissions',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Wagtail permissions...'))
        
        # Get or create Editors group
        if options['create_editors_group']:
            self.create_editors_group()
        
        # Get or create Moderators group
        if options['create_moderators_group']:
            self.create_moderators_group()
        
        # Grant access to all staff users
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        
        for user in staff_users:
            # Superusers already have all permissions
            if user.is_superuser:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Superuser {user.username} already has full access'
                    )
                )
                continue
            
            # Add user to Editors group if it exists
            try:
                editors_group = Group.objects.get(name='Editors')
                user.groups.add(editors_group)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Added {user.username} to Editors group'
                    )
                )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ Editors group not found. Use --create-editors-group'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nWagtail permissions setup complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total staff users configured: {staff_users.count()}'
            )
        )

    def create_editors_group(self):
        """Create an Editors group with standard editing permissions."""
        group, created = Group.objects.get_or_create(name='Editors')
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Created Editors group'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Editors group already exists'))
        
        # Add Wagtail admin access permission
        wagtail_admin_permission = Permission.objects.filter(
            codename='access_admin'
        ).first()
        
        if wagtail_admin_permission:
            group.permissions.add(wagtail_admin_permission)
        
        # Add page editing permissions
        page_ct = ContentType.objects.get_for_model(Page)
        page_permissions = Permission.objects.filter(
            content_type=page_ct,
            codename__in=['add_page', 'change_page', 'delete_page']
        )
        group.permissions.add(*page_permissions)
        
        # Add collection permissions
        collection_ct = ContentType.objects.get_for_model(Collection)
        collection_permissions = Permission.objects.filter(
            content_type=collection_ct
        )
        group.permissions.add(*collection_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(
                '  ✓ Configured Editors group permissions'
            )
        )

    def create_moderators_group(self):
        """Create a Moderators group with publish/unpublish permissions."""
        group, created = Group.objects.get_or_create(name='Moderators')
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Created Moderators group'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Moderators group already exists'))
        
        # Add all Editors permissions
        editors_group = Group.objects.filter(name='Editors').first()
        if editors_group:
            group.permissions.add(*editors_group.permissions.all())
        
        # Add publishing permissions
        page_ct = ContentType.objects.get_for_model(Page)
        publish_permissions = Permission.objects.filter(
            content_type=page_ct,
            codename__in=['publish_page']
        )
        group.permissions.add(*publish_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(
                '  ✓ Configured Moderators group permissions'
            )
        )

