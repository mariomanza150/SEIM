"""
Test Grades Services

Comprehensive tests for grade translation and conversion logic.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase

from grades.models import GradeScale, GradeTranslation, GradeValue
from grades.services import GradeTranslationService

User = get_user_model()


@pytest.mark.django_db
class TestGradeTranslationService(TestCase):
    """Test grade translation service methods."""

    def setUp(self):
        """Set up test data with two grade scales."""
        # Create US 4.0 GPA Scale
        self.us_scale = GradeScale.objects.create(
            name="US GPA 4.0 Scale",
            code="US_GPA_4",
            country="United States",
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        
        # Create US grade values
        self.us_a = GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="A",
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        self.us_b = GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="B",
            numeric_value=3.0,
            gpa_equivalent=3.0,
            order=2
        )
        
        self.us_c = GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="C",
            numeric_value=2.0,
            gpa_equivalent=2.0,
            order=3
        )
        
        # Create ECTS Scale
        self.ects_scale = GradeScale.objects.create(
            name="ECTS Grading Scale",
            code="ECTS",
            country="Europe",
            min_value=0.0,
            max_value=100.0,
            passing_value=50.0
        )
        
        # Create ECTS grade values
        self.ects_a = GradeValue.objects.create(
            grade_scale=self.ects_scale,
            label="A",
            numeric_value=90.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        self.ects_b = GradeValue.objects.create(
            grade_scale=self.ects_scale,
            label="B",
            numeric_value=75.0,
            gpa_equivalent=3.0,
            order=2
        )
        
        self.ects_c = GradeValue.objects.create(
            grade_scale=self.ects_scale,
            label="C",
            numeric_value=60.0,
            gpa_equivalent=2.0,
            order=3
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_translate_grade_same_scale(self):
        """Test translation within same scale returns same grade."""
        result = GradeTranslationService.translate_grade(
            source_grade_value_id=str(self.us_a.id),
            target_scale_id=str(self.us_scale.id)
        )
        
        self.assertEqual(result.id, self.us_a.id)

    def test_translate_grade_with_direct_translation(self):
        """Test translation using direct mapping."""
        # Create direct translation
        GradeTranslation.objects.create(
            source_grade=self.us_a,
            target_grade=self.ects_a,
            confidence=1.0
        )
        
        result = GradeTranslationService.translate_grade(
            source_grade_value_id=str(self.us_a.id),
            target_scale_id=str(self.ects_scale.id)
        )
        
        self.assertEqual(result.id, self.ects_a.id)

    def test_translate_grade_by_gpa_equivalent(self):
        """Test translation using GPA equivalent fallback."""
        # No direct translation, should use GPA equivalent
        result = GradeTranslationService.translate_grade(
            source_grade_value_id=str(self.us_b.id),
            target_scale_id=str(self.ects_scale.id),
            fallback_to_gpa=True
        )
        
        # Should find ECTS B (closest GPA equivalent to US B)
        self.assertEqual(result.id, self.ects_b.id)

    def test_translate_grade_no_fallback(self):
        """Test translation returns None when fallback disabled."""
        result = GradeTranslationService.translate_grade(
            source_grade_value_id=str(self.us_a.id),
            target_scale_id=str(self.ects_scale.id),
            fallback_to_gpa=False
        )
        
        # No direct translation and fallback disabled
        self.assertIsNone(result)

    def test_translate_grade_source_not_found(self):
        """Test translation with non-existent source grade."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.translate_grade(
                source_grade_value_id=fake_id,
                target_scale_id=str(self.ects_scale.id)
            )

    def test_translate_grade_target_scale_not_found(self):
        """Test translation with non-existent target scale."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.translate_grade(
                source_grade_value_id=str(self.us_a.id),
                target_scale_id=fake_id
            )

    def test_translate_by_gpa_equivalent_exact_match(self):
        """Test GPA equivalent translation with exact match."""
        result = GradeTranslationService._translate_by_gpa_equivalent(
            self.us_a, self.ects_scale
        )
        
        # US A (4.0 GPA) should match ECTS A (4.0 GPA)
        self.assertEqual(result.id, self.ects_a.id)

    def test_translate_by_gpa_equivalent_closest_match(self):
        """Test GPA equivalent translation finds closest match."""
        # Create a grade with GPA 3.5
        us_b_plus = GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="B+",
            numeric_value=3.5,
            gpa_equivalent=3.5,
            order=2
        )
        
        result = GradeTranslationService._translate_by_gpa_equivalent(
            us_b_plus, self.ects_scale
        )
        
        # Should find closest match (ECTS A at 4.0 is closer than ECTS B at 3.0)
        self.assertIsNotNone(result)

    def test_translate_by_gpa_equivalent_empty_target(self):
        """Test GPA translation with empty target scale."""
        empty_scale = GradeScale.objects.create(
            name="Empty Scale",
            code="EMPTY",
            min_value=0.0,
            max_value=10.0,
            passing_value=5.0
        )
        
        result = GradeTranslationService._translate_by_gpa_equivalent(
            self.us_a, empty_scale
        )
        
        self.assertIsNone(result)

    def test_get_gpa_equivalent_success(self):
        """Test getting GPA equivalent of a grade."""
        gpa = GradeTranslationService.get_gpa_equivalent(str(self.us_a.id))
        
        self.assertEqual(gpa, 4.0)

    def test_get_gpa_equivalent_not_found(self):
        """Test getting GPA equivalent with non-existent grade."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.get_gpa_equivalent(fake_id)

    def test_convert_gpa_to_scale_exact_match(self):
        """Test converting numeric GPA to grade with exact match."""
        result = GradeTranslationService.convert_gpa_to_scale(
            gpa_value=3.0,
            target_scale_id=str(self.us_scale.id)
        )
        
        self.assertEqual(result.id, self.us_b.id)

    def test_convert_gpa_to_scale_closest_match(self):
        """Test converting GPA finds closest grade."""
        result = GradeTranslationService.convert_gpa_to_scale(
            gpa_value=3.7,  # Between B (3.0) and A (4.0)
            target_scale_id=str(self.us_scale.id)
        )
        
        # Should find A (closer to 3.7)
        self.assertEqual(result.id, self.us_a.id)

    def test_convert_gpa_to_scale_invalid_gpa(self):
        """Test converting invalid GPA value."""
        with self.assertRaises(ValidationError):
            GradeTranslationService.convert_gpa_to_scale(
                gpa_value=5.0,  # Above 4.0
                target_scale_id=str(self.us_scale.id)
            )
        
        with self.assertRaises(ValidationError):
            GradeTranslationService.convert_gpa_to_scale(
                gpa_value=-1.0,  # Below 0.0
                target_scale_id=str(self.us_scale.id)
            )

    def test_convert_gpa_to_scale_not_found(self):
        """Test converting GPA with non-existent scale."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.convert_gpa_to_scale(
                gpa_value=3.0,
                target_scale_id=fake_id
            )

    def test_convert_gpa_to_scale_empty_scale(self):
        """Test converting GPA to empty scale."""
        empty_scale = GradeScale.objects.create(
            name="Empty Scale",
            code="EMPTY2",
            min_value=0.0,
            max_value=10.0,
            passing_value=5.0
        )
        
        result = GradeTranslationService.convert_gpa_to_scale(
            gpa_value=3.0,
            target_scale_id=str(empty_scale.id)
        )
        
        self.assertIsNone(result)

    def test_get_available_translations_with_direct(self):
        """Test getting available translations with direct mapping."""
        GradeTranslation.objects.create(
            source_grade=self.us_a,
            target_grade=self.ects_a,
            confidence=0.95,
            notes="Direct equivalence"
        )
        
        translations = GradeTranslationService.get_available_translations(
            str(self.us_a.id)
        )
        
        self.assertEqual(len(translations), 1)
        self.assertEqual(translations[0]['target_scale'], "ECTS Grading Scale")
        self.assertEqual(translations[0]['target_scale_code'], "ECTS")
        self.assertEqual(translations[0]['target_grade'], "A")
        self.assertEqual(translations[0]['target_gpa'], 4.0)
        self.assertEqual(translations[0]['method'], 'direct')
        self.assertEqual(translations[0]['confidence'], 0.95)

    def test_get_available_translations_multiple(self):
        """Test getting multiple available translations."""
        # Create another scale
        uk_scale = GradeScale.objects.create(
            name="UK Scale",
            code="UK",
            min_value=0.0,
            max_value=100.0,
            passing_value=40.0
        )
        
        uk_first = GradeValue.objects.create(
            grade_scale=uk_scale,
            label="First Class",
            numeric_value=70.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        # Create translations to both scales
        GradeTranslation.objects.create(
            source_grade=self.us_a,
            target_grade=self.ects_a,
            confidence=0.95
        )
        
        GradeTranslation.objects.create(
            source_grade=self.us_a,
            target_grade=uk_first,
            confidence=0.90
        )
        
        translations = GradeTranslationService.get_available_translations(
            str(self.us_a.id)
        )
        
        self.assertEqual(len(translations), 2)

    def test_get_available_translations_not_found(self):
        """Test getting translations for non-existent grade."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.get_available_translations(fake_id)

    def test_suggest_translation_success(self):
        """Test suggesting a new translation."""
        translation = GradeTranslationService.suggest_translation(
            source_grade_id=str(self.us_a.id),
            target_grade_id=str(self.ects_a.id),
            notes="Test translation",
            user=self.user
        )
        
        self.assertIsNotNone(translation.id)
        self.assertEqual(translation.source_grade.id, self.us_a.id)
        self.assertEqual(translation.target_grade.id, self.ects_a.id)
        self.assertEqual(translation.notes, "Test translation")
        self.assertEqual(translation.created_by, self.user)
        self.assertGreaterEqual(translation.confidence, 0.0)
        self.assertLessEqual(translation.confidence, 1.0)

    def test_suggest_translation_calculates_confidence(self):
        """Test that confidence is calculated from GPA difference."""
        translation = GradeTranslationService.suggest_translation(
            source_grade_id=str(self.us_a.id),
            target_grade_id=str(self.ects_a.id)
        )
        
        # Same GPA (4.0 = 4.0) should have high confidence
        self.assertEqual(translation.confidence, 1.0)
        
        # Different GPA should have lower confidence
        translation2 = GradeTranslationService.suggest_translation(
            source_grade_id=str(self.us_a.id),
            target_grade_id=str(self.ects_b.id)
        )
        
        self.assertLess(translation2.confidence, 1.0)

    def test_suggest_translation_same_scale(self):
        """Test suggesting translation within same scale fails."""
        with self.assertRaises(ValidationError):
            GradeTranslationService.suggest_translation(
                source_grade_id=str(self.us_a.id),
                target_grade_id=str(self.us_b.id)
            )

    def test_suggest_translation_updates_existing(self):
        """Test that suggesting existing translation updates it."""
        # Create initial translation
        trans1 = GradeTranslationService.suggest_translation(
            source_grade_id=str(self.us_a.id),
            target_grade_id=str(self.ects_a.id),
            notes="First version"
        )
        
        # Suggest again with new notes
        trans2 = GradeTranslationService.suggest_translation(
            source_grade_id=str(self.us_a.id),
            target_grade_id=str(self.ects_a.id),
            notes="Updated version",
            user=self.user
        )
        
        # Should be same object (updated, not created)
        self.assertEqual(trans1.id, trans2.id)
        trans2.refresh_from_db()
        self.assertEqual(trans2.notes, "Updated version")
        self.assertEqual(trans2.created_by, self.user)

    def test_suggest_translation_grade_not_found(self):
        """Test suggesting translation with non-existent grade."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.suggest_translation(
                source_grade_id=fake_id,
                target_grade_id=str(self.ects_a.id)
            )

    def test_check_eligibility_with_translation_eligible(self):
        """Test eligibility check when student meets requirement."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=4.0,
            student_scale_id=str(self.us_scale.id),
            required_gpa=3.0,
            required_scale_id=str(self.us_scale.id)
        )
        
        self.assertTrue(result['eligible'])
        self.assertEqual(result['student_gpa_equivalent'], 4.0)
        self.assertEqual(result['required_gpa_equivalent'], 3.0)
        self.assertEqual(result['reason'], 'Meets requirement')

    def test_check_eligibility_with_translation_not_eligible(self):
        """Test eligibility check when student doesn't meet requirement."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=2.0,
            student_scale_id=str(self.us_scale.id),
            required_gpa=3.0,
            required_scale_id=str(self.us_scale.id)
        )
        
        self.assertFalse(result['eligible'])
        self.assertEqual(result['student_gpa_equivalent'], 2.0)
        self.assertEqual(result['required_gpa_equivalent'], 3.0)
        self.assertEqual(result['reason'], 'Does not meet requirement')

    def test_check_eligibility_cross_scale(self):
        """Test eligibility check across different scales."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=90.0,  # ECTS A
            student_scale_id=str(self.ects_scale.id),
            required_gpa=3.0,  # US B
            required_scale_id=str(self.us_scale.id)
        )
        
        # ECTS A (4.0 GPA equiv) >= US B (3.0 GPA equiv)
        self.assertTrue(result['eligible'])

    def test_check_eligibility_student_grade_not_found(self):
        """Test eligibility when student grade not in scale."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=99.9,  # Not in scale
            student_scale_id=str(self.us_scale.id),
            required_gpa=3.0,
            required_scale_id=str(self.us_scale.id)
        )
        
        # Should try to find closest grade
        self.assertIsNotNone(result)

    def test_check_eligibility_required_grade_not_found(self):
        """Test eligibility when required grade not in scale."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=4.0,
            student_scale_id=str(self.us_scale.id),
            required_gpa=99.9,  # Not in scale
            required_scale_id=str(self.us_scale.id)
        )
        
        self.assertIsNotNone(result)

    def test_check_eligibility_scale_not_found(self):
        """Test eligibility with non-existent scale."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.check_eligibility_with_translation(
                student_gpa=4.0,
                student_scale_id=fake_id,
                required_gpa=3.0,
                required_scale_id=str(self.us_scale.id)
            )

    def test_find_closest_grade_exact_match(self):
        """Test finding closest grade with exact match."""
        result = GradeTranslationService._find_closest_grade(
            numeric_value=4.0,
            grade_scale=self.us_scale
        )
        
        self.assertEqual(result.id, self.us_a.id)

    def test_find_closest_grade_approximate(self):
        """Test finding closest grade with approximation."""
        result = GradeTranslationService._find_closest_grade(
            numeric_value=3.7,  # Between B (3.0) and A (4.0)
            grade_scale=self.us_scale
        )
        
        # Should find A (closer to 3.7)
        self.assertEqual(result.id, self.us_a.id)

    def test_find_closest_grade_empty_scale(self):
        """Test finding closest grade in empty scale."""
        empty_scale = GradeScale.objects.create(
            name="Empty Scale",
            code="EMPTY3",
            min_value=0.0,
            max_value=10.0,
            passing_value=5.0
        )
        
        result = GradeTranslationService._find_closest_grade(
            numeric_value=5.0,
            grade_scale=empty_scale
        )
        
        self.assertIsNone(result)

    def test_bulk_create_translations_success(self):
        """Test creating multiple translations at once."""
        mapping = {
            'A': 'A',
            'B': 'B',
            'C': 'C'
        }
        
        translations = GradeTranslationService.bulk_create_translations(
            source_scale_id=str(self.us_scale.id),
            target_scale_id=str(self.ects_scale.id),
            mapping=mapping,
            user=self.user
        )
        
        self.assertEqual(len(translations), 3)
        
        # Verify each translation
        for trans in translations:
            self.assertEqual(trans.created_by, self.user)
            self.assertIn("Bulk created", trans.notes)

    def test_bulk_create_translations_partial(self):
        """Test bulk create skips missing grades."""
        mapping = {
            'A': 'A',
            'B': 'B',
            'D': 'D',  # Doesn't exist in either scale
            'F': 'F'   # Doesn't exist in either scale
        }
        
        translations = GradeTranslationService.bulk_create_translations(
            source_scale_id=str(self.us_scale.id),
            target_scale_id=str(self.ects_scale.id),
            mapping=mapping
        )
        
        # Should create 2 translations (A and B), skip D and F
        self.assertEqual(len(translations), 2)

    def test_bulk_create_translations_scale_not_found(self):
        """Test bulk create with non-existent scale."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(ObjectDoesNotExist):
            GradeTranslationService.bulk_create_translations(
                source_scale_id=fake_id,
                target_scale_id=str(self.ects_scale.id),
                mapping={'A': 'A'}
            )

    def test_bulk_create_translations_empty_mapping(self):
        """Test bulk create with empty mapping."""
        translations = GradeTranslationService.bulk_create_translations(
            source_scale_id=str(self.us_scale.id),
            target_scale_id=str(self.ects_scale.id),
            mapping={}
        )
        
        self.assertEqual(len(translations), 0)

