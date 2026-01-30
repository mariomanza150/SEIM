"""
Wagtail Hooks

Custom hooks for Wagtail admin interface customization,
including branding, menu items, and dashboard widgets.
"""

from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """Add custom CSS to Wagtail admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/wagtail_admin_custom.css')
    )


@hooks.register('insert_editor_js')
def editor_js():
    """Add custom JavaScript to Wagtail page editor."""
    return format_html(
        '<script src="{}"></script>',
        static('js/wagtail_editor_custom.js')
    )


@hooks.register('construct_main_menu')
def add_django_admin_menu_item(request, menu_items):
    """Add link to Django admin in Wagtail menu for system admins."""
    # Only show for superusers or users with admin role
    if request.user.is_superuser or (hasattr(request.user, 'has_role') and request.user.has_role('admin')):
        menu_items.append(
            MenuItem(
                'Django Admin',
                reverse('admin:index'),
                icon_name='cog',
                order=10000
            )
        )


# Dashboard panels can be added here in the future
# Note: In Wagtail 6.3+, the dashboard panel API has changed
# @hooks.register('construct_homepage_panels')
# def add_seim_dashboard_panel(request, panels):
#     """Add SEIM-specific dashboard panel."""
#     pass


@hooks.register('insert_global_admin_js')
def global_admin_js():
    """Add custom global JavaScript to Wagtail admin."""
    return format_html(
        '''
        <script>
            // Set custom branding
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('SEIM Wagtail Admin loaded');
            }});
        </script>
        '''
    )


# Restrict Wagtail admin access based on roles
@hooks.register('construct_wagtail_userbar')
def hide_userbar_for_non_editors(request, items):
    """Hide Wagtail userbar for users without edit permissions."""
    if not request.user.is_authenticated:
        items.clear()
        return
    
    # Keep userbar only for staff, superusers, and users with coordinator/admin roles
    if not (request.user.is_staff or request.user.is_superuser or 
            (hasattr(request.user, 'has_role') and 
             (request.user.has_role('admin') or request.user.has_role('coordinator')))):
        items.clear()

