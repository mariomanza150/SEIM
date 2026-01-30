"""
Management command to create test exchange programs for Vue.js testing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from exchange.models import Program


class Command(BaseCommand):
    help = "Create test exchange programs for development and testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating test exchange programs...")

        # Test programs data
        programs_data = [
            {
                "name": "Erasmus+ Exchange - University of Barcelona, Spain",
                "description": "Study abroad program at the University of Barcelona. Experience Mediterranean culture while pursuing your academic goals. Courses available in English and Spanish. Duration: 1 Semester.",
                "start_date": timezone.now().date() + timedelta(days=60),
                "end_date": timezone.now().date() + timedelta(days=240),
                "min_gpa": 3.0,
                "required_language": "Spanish",
                "min_language_level": "B1",
                "is_active": True,
            },
            {
                "name": "DAAD Exchange - Technical University of Munich, Germany",
                "description": "Engineering and sciences exchange program in Munich. World-class technical education with strong industry connections. Courses primarily in English. Duration: 1 Academic Year.",
                "start_date": timezone.now().date() + timedelta(days=90),
                "end_date": timezone.now().date() + timedelta(days=455),
                "min_gpa": 3.3,
                "required_language": "German",
                "min_language_level": "A2",
                "is_active": True,
            },
            {
                "name": "Fulbright Program - Harvard University, USA",
                "description": "Prestigious exchange program at Harvard University. Open to all disciplines. Highly competitive with comprehensive scholarship support. Duration: 2 Semesters.",
                "start_date": timezone.now().date() + timedelta(days=120),
                "end_date": timezone.now().date() + timedelta(days=485),
                "min_gpa": 3.7,
                "required_language": "English",
                "min_language_level": "C1",
                "is_active": True,
            },
            {
                "name": "Exchange Program - University of Tokyo, Japan",
                "description": "Cultural and academic exchange in Tokyo. Intensive Japanese language courses available. Mix of humanities and sciences. Duration: 1 Semester.",
                "start_date": timezone.now().date() + timedelta(days=75),
                "end_date": timezone.now().date() + timedelta(days=255),
                "min_gpa": 3.2,
                "required_language": "Japanese",
                "min_language_level": "B1",
                "is_active": True,
            },
            {
                "name": "Sorbonne Exchange - Paris, France",
                "description": "Liberal arts and humanities program at Sorbonne University. Immerse yourself in French culture and language in the heart of Paris. Duration: 1 Semester.",
                "start_date": timezone.now().date() + timedelta(days=50),
                "end_date": timezone.now().date() + timedelta(days=230),
                "min_gpa": 2.8,
                "required_language": "French",
                "min_language_level": "B2",
                "is_active": True,
            },
            {
                "name": "Sciences Po Exchange - Paris, France",
                "description": "Political science and international relations program. Taught in English. Strong focus on European politics and policy. Duration: 1 Academic Year.",
                "start_date": timezone.now().date() + timedelta(days=100),
                "end_date": timezone.now().date() + timedelta(days=465),
                "min_gpa": 3.4,
                "required_language": "English",
                "min_language_level": "C1",
                "is_active": True,
            },
        ]

        created_count = 0
        updated_count = 0

        for program_data in programs_data:
            name = program_data["name"]
            
            program, created = Program.objects.update_or_create(
                name=name,
                defaults=program_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {name}")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  ↻ Updated: {name}")
                )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} new programs"))
        self.stdout.write(self.style.WARNING(f"↻ Updated {updated_count} existing programs"))
        self.stdout.write("=" * 70)
        self.stdout.write("\nTest programs are now available at:")
        self.stdout.write("  API: http://localhost:8001/api/programs/")
        self.stdout.write("  Vue: http://localhost:5173/applications/new")
        self.stdout.write("\n")
