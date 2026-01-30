"""
Management command to test URL routing and accessibility.
"""

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Test URL routing and accessibility'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing URL Structure...'))
        
        client = Client()
        
        # Test public URLs (should be accessible without login)
        public_urls = [
            ('/', 'Homepage (CMS)'),
            ('/cms/', 'Wagtail Admin Login'),
            ('/seim/login/', 'SEIM Login'),
            ('/seim/register/', 'SEIM Registration'),
            ('/api/', 'API Root'),
            ('/health/', 'Health Check'),
        ]
        
        self.stdout.write(self.style.SUCCESS('\n📍 Testing Public URLs:'))
        for url, description in public_urls:
            response = client.get(url, follow=True)
            status = '✓' if response.status_code in [200, 302] else '✗'
            color = self.style.SUCCESS if status == '✓' else self.style.ERROR
            self.stdout.write(
                color(f'  {status} {url:40s} - {description} ({response.status_code})')
            )
        
        # Test authenticated URLs (requires login)
        # Try to create a test user if it doesn't exist
        try:
            test_user = User.objects.filter(username='test_user').first()
            if not test_user:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠ No test user found. Skipping authenticated URL tests.'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        '  Create a user to test authenticated URLs.'
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS('\n🔒 Testing Authenticated URLs:'))
                client.force_login(test_user)
                
                auth_urls = [
                    ('/seim/dashboard/', 'Dashboard'),
                    ('/seim/profile/', 'Profile'),
                    ('/seim/applications/', 'Applications List'),
                ]
                
                for url, description in auth_urls:
                    response = client.get(url, follow=True)
                    status = '✓' if response.status_code == 200 else '✗'
                    color = self.style.SUCCESS if status == '✓' else self.style.ERROR
                    self.stdout.write(
                        color(f'  {status} {url:40s} - {description} ({response.status_code})')
                    )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ Error testing authenticated URLs: {e}')
            )
        
        # Test admin URLs
        try:
            staff_user = User.objects.filter(is_staff=True).first()
            if staff_user:
                self.stdout.write(self.style.SUCCESS('\n👨‍💼 Testing Admin URLs:'))
                client.force_login(staff_user)
                
                admin_urls = [
                    ('/seim/admin/', 'Django Admin'),
                    ('/cms/', 'Wagtail Admin'),
                ]
                
                for url, description in admin_urls:
                    response = client.get(url, follow=True)
                    status = '✓' if response.status_code == 200 else '✗'
                    color = self.style.SUCCESS if status == '✓' else self.style.ERROR
                    self.stdout.write(
                        color(f'  {status} {url:40s} - {description} ({response.status_code})')
                    )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'\n⚠ Error testing admin URLs: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ URL structure test complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\nURL Structure:'
            )
        )
        self.stdout.write('  • CMS (public): /')
        self.stdout.write('  • SEIM App: /seim/')
        self.stdout.write('  • Wagtail Admin: /cms/')
        self.stdout.write('  • Django Admin: /seim/admin/')
        self.stdout.write('  • APIs: /api/')

