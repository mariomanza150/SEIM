"""Tests for grade translation system."""
import pytest
from django.core.exceptions import ValidationError

from accounts.models import Profile, User
from grades.models import GradeScale, GradeTranslation, GradeValue
from grades.services import GradeTranslationService


@pytest.mark.django_db
class TestGradeScale:
    """Tests for GradeScale model."""

    def test_create_grade_scale(self):
        """Test creating a grade scale."""
        scale = GradeScale.objects.create(
            name='Test Scale',
            code='TEST',
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        assert scale.name == 'Test Scale'
        assert scale.code == 'TEST'
        assert scale.is_active is True

    def test_grade_scale_validation(self):
        """Test grade scale validation."""
        scale = GradeScale(
            name='Invalid Scale',
            code='INVALID',
            min_value=4.0,
            max_value=0.0,  # Invalid: max < min
            passing_value=2.0
        )
        with pytest.raises(ValidationError):
            scale.clean()

    def test_grade_scale_str(self):
        """Test string representation."""
        scale = GradeScale.objects.create(
            name='Test Scale',
            code='TEST',
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        assert str(scale) == 'Test Scale (TEST)'


@pytest.mark.django_db
class TestGradeValue:
    """Tests for GradeValue model."""

    def test_create_grade_value(self):
        """Test creating a grade value."""
        scale = GradeScale.objects.create(
            name='Test Scale',
            code='TEST',
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        grade = GradeValue.objects.create(
            grade_scale=scale,
            label='A',
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1
        )
        assert grade.label == 'A'
        assert grade.numeric_value == 4.0
        assert grade.is_passing is True

    def test_grade_value_unique_constraint(self):
        """Test unique constraint on label within scale."""
        scale = GradeScale.objects.create(
            name='Test Scale',
            code='TEST',
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        GradeValue.objects.create(
            grade_scale=scale,
            label='A',
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1
        )
        # Creating another 'A' grade in same scale should fail
        with pytest.raises(Exception):  # IntegrityError
            GradeValue.objects.create(
                grade_scale=scale,
                label='A',
                numeric_value=3.7,
                gpa_equivalent=3.7,
                order=2
            )


@pytest.mark.django_db
class TestGradeTranslation:
    """Tests for GradeTranslation model."""

    def test_create_translation(self):
        """Test creating a grade translation."""
        us_scale = GradeScale.objects.create(
            name='US GPA', code='US', min_value=0.0, max_value=4.0, passing_value=2.0
        )
        ects_scale = GradeScale.objects.create(
            name='ECTS', code='ECTS', min_value=0.0, max_value=5.0, passing_value=2.0
        )

        us_a = GradeValue.objects.create(
            grade_scale=us_scale, label='A', numeric_value=4.0, gpa_equivalent=4.0, order=1
        )
        ects_a = GradeValue.objects.create(
            grade_scale=ects_scale, label='A', numeric_value=5.0, gpa_equivalent=4.0, order=1
        )

        translation = GradeTranslation.objects.create(
            source_grade=us_a,
            target_grade=ects_a,
            confidence=1.0
        )

        assert translation.source_grade == us_a
        assert translation.target_grade == ects_a
        assert translation.confidence == 1.0

    def test_translation_validation(self):
        """Test translation validation (same scale not allowed)."""
        scale = GradeScale.objects.create(
            name='Test', code='TEST', min_value=0.0, max_value=4.0, passing_value=2.0
        )

        grade_a = GradeValue.objects.create(
            grade_scale=scale, label='A', numeric_value=4.0, gpa_equivalent=4.0, order=1
        )
        grade_b = GradeValue.objects.create(
            grade_scale=scale, label='B', numeric_value=3.0, gpa_equivalent=3.0, order=2
        )

        translation = GradeTranslation(source_grade=grade_a, target_grade=grade_b)
        with pytest.raises(ValidationError):
            translation.clean()


@pytest.mark.django_db
class TestGradeTranslationService:
    """Tests for GradeTranslationService."""

    def setup_method(self):
        """Set up test data."""
        # Create US scale
        self.us_scale = GradeScale.objects.create(
            name='US GPA', code='US', min_value=0.0, max_value=4.0, passing_value=2.0
        )
        self.us_a = GradeValue.objects.create(
            grade_scale=self.us_scale, label='A', numeric_value=4.0,
            gpa_equivalent=4.0, order=1
        )
        self.us_b = GradeValue.objects.create(
            grade_scale=self.us_scale, label='B', numeric_value=3.0,
            gpa_equivalent=3.0, order=2
        )

        # Create ECTS scale
        self.ects_scale = GradeScale.objects.create(
            name='ECTS', code='ECTS', min_value=0.0, max_value=5.0, passing_value=2.0
        )
        self.ects_a = GradeValue.objects.create(
            grade_scale=self.ects_scale, label='A', numeric_value=5.0,
            gpa_equivalent=4.0, order=1
        )
        self.ects_b = GradeValue.objects.create(
            grade_scale=self.ects_scale, label='B', numeric_value=4.0,
            gpa_equivalent=3.5, order=2
        )

    def test_translate_grade_same_scale(self):
        """Test translating grade within same scale returns same grade."""
        result = GradeTranslationService.translate_grade(
            str(self.us_a.id), str(self.us_scale.id)
        )
        assert result == self.us_a

    def test_translate_grade_with_gpa_equivalent(self):
        """Test translating grade using GPA equivalent."""
        result = GradeTranslationService.translate_grade(
            str(self.us_a.id), str(self.ects_scale.id)
        )
        assert result is not None
        assert result.gpa_equivalent == 4.0  # Should find ECTS A

    def test_translate_grade_direct_translation(self):
        """Test translating with direct translation mapping."""
        # Create direct translation
        GradeTranslation.objects.create(
            source_grade=self.us_b,
            target_grade=self.ects_b,
            confidence=1.0
        )

        result = GradeTranslationService.translate_grade(
            str(self.us_b.id), str(self.ects_scale.id)
        )
        assert result == self.ects_b

    def test_get_gpa_equivalent(self):
        """Test getting GPA equivalent."""
        gpa = GradeTranslationService.get_gpa_equivalent(str(self.us_a.id))
        assert gpa == 4.0

    def test_convert_gpa_to_scale(self):
        """Test converting numeric GPA to grade in scale."""
        result = GradeTranslationService.convert_gpa_to_scale(3.5, str(self.ects_scale.id))
        assert result == self.ects_b  # Should find ECTS B with GPA 3.5

    def test_check_eligibility_with_translation(self):
        """Test eligibility check with grade translation."""
        result = GradeTranslationService.check_eligibility_with_translation(
            student_gpa=4.0,
            student_scale_id=str(self.us_scale.id),
            required_gpa=5.0,
            required_scale_id=str(self.ects_scale.id)
        )

        assert result['eligible'] is True
        assert result['student_gpa_equivalent'] == 4.0
        assert result['required_gpa_equivalent'] == 4.0

    def test_suggest_translation(self):
        """Test suggesting a translation."""
        translation = GradeTranslationService.suggest_translation(
            str(self.us_a.id),
            str(self.ects_a.id)
        )

        assert translation.source_grade == self.us_a
        assert translation.target_grade == self.ects_a
        assert translation.confidence == 1.0  # Same GPA equivalent

    def test_bulk_create_translations(self):
        """Test bulk creating translations."""
        mapping = {
            'A': 'A',
            'B': 'B'
        }

        translations = GradeTranslationService.bulk_create_translations(
            str(self.us_scale.id),
            str(self.ects_scale.id),
            mapping
        )

        assert len(translations) == 2
        assert all(isinstance(t, GradeTranslation) for t in translations)


@pytest.mark.django_db
class TestProfileGradeIntegration:
    """Test integration of grade translation with user profiles."""

    def setup_method(self):
        """Set up test data."""
        # Create grade scale
        self.german_scale = GradeScale.objects.create(
            name='German Scale',
            code='GERMAN',
            min_value=1.0,
            max_value=5.0,
            passing_value=4.0,
            is_reverse_scale=True
        )

        # Create grade value (1.0 in German = 4.0 GPA)
        self.german_1_0 = GradeValue.objects.create(
            grade_scale=self.german_scale,
            label='1.0',
            numeric_value=1.0,
            gpa_equivalent=4.0,
            order=1
        )

    def test_profile_get_gpa_equivalent(self):
        """Test getting GPA equivalent from profile."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        profile = Profile.objects.get(user=user)
        profile.gpa = 1.0
        profile.grade_scale = self.german_scale
        profile.save()

        gpa_equiv = profile.get_gpa_equivalent()
        assert gpa_equiv == 4.0  # German 1.0 = GPA 4.0
