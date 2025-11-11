"""Management command to verify grade translation integration."""
from django.contrib import admin
from django.core.management.base import BaseCommand

from accounts.models import Profile, User
from exchange.models import ApplicationStatus, Program
from exchange.services import ApplicationService
from grades.models import GradeScale


class Command(BaseCommand):
    help = 'Verify grade translation integration with profiles and applications'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.MIGRATE_HEADING('GRADE TRANSLATION INTEGRATION VERIFICATION'))
        self.stdout.write('='*60)

        # TEST 1: Admin Registration
        self.stdout.write('\n=== TEST 1: Admin Registration ===')
        registered_models = [
            f"{m._meta.app_label}.{m._meta.object_name}"
            for m in admin.site._registry.keys()
        ]

        assert 'grades.GradeScale' in registered_models, "GradeScale not registered"
        assert 'grades.GradeValue' in registered_models, "GradeValue not registered"
        assert 'grades.GradeTranslation' in registered_models, "GradeTranslation not registered"

        self.stdout.write('✓ GradeScale registered')
        self.stdout.write('✓ GradeValue registered')
        self.stdout.write('✓ GradeTranslation registered')
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 2: Profile Integration
        self.stdout.write('\n=== TEST 2: Profile Integration ===')

        # Clean up any existing test users
        User.objects.filter(username__startswith='test_').delete()

        # Create test user
        user = User.objects.create_user(
            username='test_german_student',
            email='test@german.edu',
            password='testpass123'
        )

        profile = Profile.objects.get(user=user)
        german_scale = GradeScale.objects.get(code='GERMAN')

        # Set German grade
        profile.grade_scale = german_scale
        profile.gpa = 1.3  # Very good in German system
        profile.save()

        # Get GPA equivalent
        gpa_equiv = profile.get_gpa_equivalent()

        self.stdout.write(f'German grade 1.3 -> {gpa_equiv:.2f} GPA equivalent')
        assert gpa_equiv == 3.7, f"Expected 3.7, got {gpa_equiv}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 3: Application Service Integration
        self.stdout.write('\n=== TEST 3: ApplicationService Eligibility Check ===')

        # Create program with US GPA requirement
        ApplicationStatus.objects.get_or_create(name='draft', defaults={'order': 0})

        program = Program.objects.create(
            name='Test Exchange Program',
            description='Test program',
            start_date='2025-09-01',
            end_date='2026-01-31',
            min_gpa=3.0  # US GPA requirement
        )

        # Test with German student (should pass with 1.3 = 3.7 GPA)
        try:
            ApplicationService.check_eligibility(user, program)
            self.stdout.write('✓ German student (1.3 = 3.7 GPA) eligible for 3.0 GPA program')
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ FAILED: {e}'))
            raise

        # TEST 4: Failing Eligibility
        self.stdout.write('\n=== TEST 4: Failing Eligibility Check ===')

        # Update profile to failing grade
        profile.gpa = 3.7  # Poor grade in German (= 1.3 GPA)
        profile.save()

        # Refresh user to get updated profile
        user.refresh_from_db()

        try:
            ApplicationService.check_eligibility(user, program)
            self.stdout.write(self.style.ERROR('❌ FAILED: Should have raised ValueError'))
            raise AssertionError("Expected ValueError")
        except ValueError as e:
            self.stdout.write(f'✓ Correctly rejected: {str(e)[:80]}...')
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 5: Backward Compatibility
        self.stdout.write('\n=== TEST 5: Backward Compatibility (No Grade Scale) ===')

        # Create user without grade scale
        user2 = User.objects.create_user(
            username='test_legacy_student',
            email='test@legacy.edu',
            password='testpass123'
        )

        profile2 = Profile.objects.get(user=user2)
        profile2.gpa = 3.5  # Direct GPA, no scale
        profile2.save()

        try:
            ApplicationService.check_eligibility(user2, program)
            self.stdout.write('✓ Legacy profile (no grade scale) works with direct GPA')
            self.stdout.write(self.style.SUCCESS('✅ PASSED'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ FAILED: {e}'))
            raise

        # Cleanup
        user.delete()
        user2.delete()
        program.delete()

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('ALL INTEGRATION TESTS PASSED! ✅'))
        self.stdout.write('='*60 + '\n')

