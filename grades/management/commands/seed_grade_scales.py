"""Management command to seed common grade scales and values."""
from django.core.management.base import BaseCommand
from django.db import transaction

from grades.models import GradeScale, GradeValue


class Command(BaseCommand):
    help = 'Seed common grade scales (US GPA, ECTS, UK, German, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing grade scales before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing grade scales...'))
            GradeScale.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all grade scales'))

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding grade scales...'))

        # 1. US GPA 4.0 Scale
        self._create_us_gpa_scale()

        # 2. ECTS (European Credit Transfer System)
        self._create_ects_scale()

        # 3. UK Classification
        self._create_uk_scale()

        # 4. German Scale (1.0-5.0)
        self._create_german_scale()

        # 5. French Scale (0-20)
        self._create_french_scale()

        # 6. Canadian Percentage Scale
        self._create_canadian_scale()

        self.stdout.write(self.style.SUCCESS('Successfully seeded all grade scales'))

    def _create_us_gpa_scale(self):
        """Create US GPA 4.0 scale."""
        scale, created = GradeScale.objects.get_or_create(
            code='US_GPA_4',
            defaults={
                'name': 'US GPA 4.0 Scale',
                'description': 'Standard US 4.0 GPA scale with letter grades',
                'country': 'United States',
                'min_value': 0.0,
                'max_value': 4.0,
                'passing_value': 2.0,
                'is_active': True,
                'is_reverse_scale': False
            }
        )

        if created:
            grades = [
                ('A', 4.0, 4.0, 93.0, 100.0, 'Excellent', 1),
                ('A-', 3.7, 3.7, 90.0, 92.9, 'Excellent', 2),
                ('B+', 3.3, 3.3, 87.0, 89.9, 'Good', 3),
                ('B', 3.0, 3.0, 83.0, 86.9, 'Good', 4),
                ('B-', 2.7, 2.7, 80.0, 82.9, 'Good', 5),
                ('C+', 2.3, 2.3, 77.0, 79.9, 'Satisfactory', 6),
                ('C', 2.0, 2.0, 73.0, 76.9, 'Satisfactory', 7),
                ('C-', 1.7, 1.7, 70.0, 72.9, 'Passing', 8),
                ('D+', 1.3, 1.3, 67.0, 69.9, 'Poor', 9),
                ('D', 1.0, 1.0, 60.0, 66.9, 'Poor', 10),
                ('F', 0.0, 0.0, 0.0, 59.9, 'Failing', 11),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric >= 2.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

    def _create_ects_scale(self):
        """Create ECTS (European) scale."""
        scale, created = GradeScale.objects.get_or_create(
            code='ECTS',
            defaults={
                'name': 'ECTS Grading Scale',
                'description': 'European Credit Transfer and Accumulation System',
                'country': 'European Union',
                'min_value': 0.0,
                'max_value': 5.0,
                'passing_value': 2.0,
                'is_active': True,
                'is_reverse_scale': False
            }
        )

        if created:
            grades = [
                ('A', 5.0, 4.0, 90.0, 100.0, 'Excellent - outstanding performance', 1),
                ('B', 4.0, 3.5, 80.0, 89.9, 'Very Good - above average', 2),
                ('C', 3.0, 3.0, 70.0, 79.9, 'Good - generally sound work', 3),
                ('D', 2.0, 2.5, 60.0, 69.9, 'Satisfactory - fair but with shortcomings', 4),
                ('E', 1.0, 2.0, 50.0, 59.9, 'Sufficient - meets minimum criteria', 5),
                ('FX', 0.5, 1.0, 40.0, 49.9, 'Fail - more work required', 6),
                ('F', 0.0, 0.0, 0.0, 39.9, 'Fail - considerable further work required', 7),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric >= 1.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

    def _create_uk_scale(self):
        """Create UK classification scale."""
        scale, created = GradeScale.objects.get_or_create(
            code='UK_CLASS',
            defaults={
                'name': 'UK Degree Classification',
                'description': 'United Kingdom university degree classification',
                'country': 'United Kingdom',
                'min_value': 0.0,
                'max_value': 100.0,
                'passing_value': 40.0,
                'is_active': True,
                'is_reverse_scale': False
            }
        )

        if created:
            grades = [
                ('First Class', 70.0, 4.0, 70.0, 100.0, 'First Class Honours', 1),
                ('Upper Second (2:1)', 60.0, 3.5, 60.0, 69.9, 'Upper Second Class Honours', 2),
                ('Lower Second (2:2)', 50.0, 3.0, 50.0, 59.9, 'Lower Second Class Honours', 3),
                ('Third Class', 40.0, 2.0, 40.0, 49.9, 'Third Class Honours', 4),
                ('Ordinary Pass', 35.0, 1.5, 35.0, 39.9, 'Pass without honours', 5),
                ('Fail', 0.0, 0.0, 0.0, 34.9, 'Fail', 6),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric >= 40.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

    def _create_german_scale(self):
        """Create German scale (1.0-5.0, lower is better)."""
        scale, created = GradeScale.objects.get_or_create(
            code='GERMAN',
            defaults={
                'name': 'German Grading Scale',
                'description': 'German university grading scale (1.0 = best, 5.0 = worst)',
                'country': 'Germany',
                'min_value': 1.0,
                'max_value': 5.0,
                'passing_value': 4.0,
                'is_active': True,
                'is_reverse_scale': True  # Lower is better
            }
        )

        if created:
            grades = [
                ('1.0', 1.0, 4.0, 95.0, 100.0, 'Sehr gut (very good)', 1),
                ('1.3', 1.3, 3.7, 90.0, 94.9, 'Sehr gut (very good)', 2),
                ('1.7', 1.7, 3.3, 85.0, 89.9, 'Gut (good)', 3),
                ('2.0', 2.0, 3.0, 80.0, 84.9, 'Gut (good)', 4),
                ('2.3', 2.3, 2.7, 75.0, 79.9, 'Gut (good)', 5),
                ('2.7', 2.7, 2.3, 70.0, 74.9, 'Befriedigend (satisfactory)', 6),
                ('3.0', 3.0, 2.0, 65.0, 69.9, 'Befriedigend (satisfactory)', 7),
                ('3.3', 3.3, 1.7, 60.0, 64.9, 'Befriedigend (satisfactory)', 8),
                ('3.7', 3.7, 1.3, 55.0, 59.9, 'Ausreichend (sufficient)', 9),
                ('4.0', 4.0, 1.0, 50.0, 54.9, 'Ausreichend (sufficient)', 10),
                ('5.0', 5.0, 0.0, 0.0, 49.9, 'Nicht ausreichend (insufficient)', 11),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric <= 4.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

    def _create_french_scale(self):
        """Create French scale (0-20)."""
        scale, created = GradeScale.objects.get_or_create(
            code='FRENCH',
            defaults={
                'name': 'French Grading Scale',
                'description': 'French university grading scale (0-20)',
                'country': 'France',
                'min_value': 0.0,
                'max_value': 20.0,
                'passing_value': 10.0,
                'is_active': True,
                'is_reverse_scale': False
            }
        )

        if created:
            grades = [
                ('18-20', 19.0, 4.0, 90.0, 100.0, 'Très bien (very good)', 1),
                ('16-17.9', 16.5, 3.7, 80.0, 89.9, 'Très bien (very good)', 2),
                ('14-15.9', 14.5, 3.3, 70.0, 79.9, 'Bien (good)', 3),
                ('12-13.9', 12.5, 3.0, 60.0, 69.9, 'Assez bien (fairly good)', 4),
                ('10-11.9', 10.5, 2.5, 50.0, 59.9, 'Passable (passing)', 5),
                ('8-9.9', 8.5, 2.0, 40.0, 49.9, 'Insuffisant (insufficient)', 6),
                ('0-7.9', 4.0, 0.0, 0.0, 39.9, 'Très insuffisant (very insufficient)', 7),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric >= 10.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

    def _create_canadian_scale(self):
        """Create Canadian percentage scale."""
        scale, created = GradeScale.objects.get_or_create(
            code='CANADIAN_PCT',
            defaults={
                'name': 'Canadian Percentage Scale',
                'description': 'Canadian university percentage grading scale',
                'country': 'Canada',
                'min_value': 0.0,
                'max_value': 100.0,
                'passing_value': 50.0,
                'is_active': True,
                'is_reverse_scale': False
            }
        )

        if created:
            grades = [
                ('A+', 95.0, 4.0, 90.0, 100.0, 'Excellent', 1),
                ('A', 87.5, 3.7, 85.0, 89.9, 'Excellent', 2),
                ('A-', 82.5, 3.3, 80.0, 84.9, 'Very Good', 3),
                ('B+', 77.5, 3.0, 75.0, 79.9, 'Good', 4),
                ('B', 72.5, 2.7, 70.0, 74.9, 'Good', 5),
                ('B-', 67.5, 2.3, 65.0, 69.9, 'Satisfactory', 6),
                ('C+', 62.5, 2.0, 60.0, 64.9, 'Satisfactory', 7),
                ('C', 57.5, 1.7, 55.0, 59.9, 'Passing', 8),
                ('C-', 52.5, 1.3, 50.0, 54.9, 'Passing', 9),
                ('D', 45.0, 1.0, 40.0, 49.9, 'Minimal Pass', 10),
                ('F', 20.0, 0.0, 0.0, 39.9, 'Fail', 11),
            ]

            for label, numeric, gpa, min_pct, max_pct, desc, order in grades:
                GradeValue.objects.create(
                    grade_scale=scale,
                    label=label,
                    numeric_value=numeric,
                    gpa_equivalent=gpa,
                    min_percentage=min_pct,
                    max_percentage=max_pct,
                    description=desc,
                    order=order,
                    is_passing=(numeric >= 50.0)
                )

            self.stdout.write(self.style.SUCCESS(f'Created {scale.name}'))

