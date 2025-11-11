"""Management command to test grade translation functionality."""
from django.core.management.base import BaseCommand

from grades.models import GradeScale, GradeValue
from grades.services import GradeTranslationService


class Command(BaseCommand):
    help = 'Test grade translation service functionality'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.MIGRATE_HEADING('GRADE TRANSLATION SERVICE VERIFICATION'))
        self.stdout.write('='*60)

        # Get scales
        us = GradeScale.objects.get(code='US_GPA_4')
        german = GradeScale.objects.get(code='GERMAN')
        ects = GradeScale.objects.get(code='ECTS')

        # TEST 1
        self.stdout.write('\n=== TEST 1: Translate German 1.3 to US Scale ===')
        german_1_3 = GradeValue.objects.get(grade_scale=german, label='1.3')
        result = GradeTranslationService.translate_grade(str(german_1_3.id), str(us.id))
        self.stdout.write(f'German 1.3 (GPA {german_1_3.gpa_equivalent}) -> US {result.label} (GPA {result.gpa_equivalent})')
        assert result.label == 'A-', f"Expected A-, got {result.label}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 2
        self.stdout.write('\n=== TEST 2: Convert GPA 3.5 to ECTS ===')
        result = GradeTranslationService.convert_gpa_to_scale(3.5, str(ects.id))
        self.stdout.write(f'GPA 3.5 -> ECTS {result.label} (GPA {result.gpa_equivalent})')
        assert result is not None, "Expected ECTS grade, got None"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 3
        self.stdout.write('\n=== TEST 3: Check Eligibility (Passing case) ===')
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=1.3,  # German grade
            student_scale_id=str(german.id),
            required_gpa=3.0,  # US requirement
            required_scale_id=str(us.id)
        )
        self.stdout.write(f'Student: {result["student_grade"]} = {result["student_gpa_equivalent"]} GPA')
        self.stdout.write(f'Required: {result["required_grade"]} = {result["required_gpa_equivalent"]} GPA')
        self.stdout.write(f'Eligible: {result["eligible"]} - {result["reason"]}')
        assert result['eligible'], f"Expected eligible=True, got {result['eligible']}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 4
        self.stdout.write('\n=== TEST 4: Check Eligibility (Failing case) ===')
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=3.7,  # German 3.7 = 1.3 GPA
            student_scale_id=str(german.id),
            required_gpa=3.0,  # US requirement
            required_scale_id=str(us.id)
        )
        self.stdout.write(f'Student: {result["student_grade"]} = {result["student_gpa_equivalent"]} GPA')
        self.stdout.write(f'Required: {result["required_grade"]} = {result["required_gpa_equivalent"]} GPA')
        self.stdout.write(f'Eligible: {result["eligible"]} - {result["reason"]}')
        assert not result['eligible'], f"Expected eligible=False, got {result['eligible']}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 5
        self.stdout.write('\n=== TEST 5: Suggest Translation ===')
        us_a = GradeValue.objects.get(grade_scale=us, label='A')
        ects_a = GradeValue.objects.get(grade_scale=ects, label='A')
        translation = GradeTranslationService.suggest_translation(
            str(us_a.id),
            str(ects_a.id),
            notes="Test translation"
        )
        self.stdout.write(f'Created translation: US {us_a.label} -> ECTS {ects_a.label}')
        self.stdout.write(f'Confidence: {translation.confidence:.2f}')
        assert translation.confidence == 1.0, f"Expected confidence 1.0, got {translation.confidence}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        # TEST 6
        self.stdout.write('\n=== TEST 6: Bulk Create Translations ===')
        mapping = {'B': 'B', 'C': 'C'}
        translations = GradeTranslationService.bulk_create_translations(
            str(us.id),
            str(ects.id),
            mapping
        )
        self.stdout.write(f'Created {len(translations)} translations')
        assert len(translations) == 2, f"Expected 2 translations, got {len(translations)}"
        self.stdout.write(self.style.SUCCESS('✅ PASSED'))

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('ALL TESTS PASSED! ✅'))
        self.stdout.write('='*60 + '\n')

