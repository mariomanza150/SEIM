"""Service layer for grade translation logic."""
from typing import Any

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import GradeScale, GradeTranslation, GradeValue


class GradeTranslationService:
    """Service for translating grades between different grading scales."""

    @staticmethod
    def translate_grade(
        source_grade_value_id: str,
        target_scale_id: str,
        fallback_to_gpa: bool = True
    ) -> GradeValue | None:
        """
        Translate a grade value to a target scale.

        Args:
            source_grade_value_id: UUID of the source grade value
            target_scale_id: UUID of the target grade scale
            fallback_to_gpa: If True, use GPA equivalent when no direct translation exists

        Returns:
            GradeValue in target scale, or None if no translation found

        Raises:
            ObjectDoesNotExist: If source grade or target scale not found
        """
        try:
            source_grade = GradeValue.objects.select_related('grade_scale').get(
                id=source_grade_value_id
            )
            target_scale = GradeScale.objects.prefetch_related('grade_values').get(
                id=target_scale_id
            )
        except GradeValue.DoesNotExist:
            raise ObjectDoesNotExist(f"Source grade value {source_grade_value_id} not found")
        except GradeScale.DoesNotExist:
            raise ObjectDoesNotExist(f"Target grade scale {target_scale_id} not found")

        # If same scale, return the same grade
        if source_grade.grade_scale_id == target_scale_id:
            return source_grade

        # Try direct translation first
        direct_translation = GradeTranslationService._get_direct_translation(
            source_grade, target_scale
        )
        if direct_translation:
            return direct_translation

        # Fallback to GPA equivalent translation
        if fallback_to_gpa:
            return GradeTranslationService._translate_by_gpa_equivalent(
                source_grade, target_scale
            )

        return None

    @staticmethod
    def _get_direct_translation(
        source_grade: GradeValue,
        target_scale: GradeScale
    ) -> GradeValue | None:
        """Get direct translation if it exists."""
        try:
            translation = GradeTranslation.objects.select_related(
                'target_grade'
            ).get(
                source_grade=source_grade,
                target_grade__grade_scale=target_scale
            )
            return translation.target_grade
        except GradeTranslation.DoesNotExist:
            return None

    @staticmethod
    def _translate_by_gpa_equivalent(
        source_grade: GradeValue,
        target_scale: GradeScale
    ) -> GradeValue | None:
        """Translate using GPA equivalent as intermediate value."""
        gpa_equiv = source_grade.gpa_equivalent

        # Find closest GPA equivalent in target scale
        target_grades = target_scale.grade_values.all().order_by('gpa_equivalent')

        if not target_grades:
            return None

        # Find the closest match
        closest_grade = None
        min_diff = float('inf')

        for grade in target_grades:
            diff = abs(grade.gpa_equivalent - gpa_equiv)
            if diff < min_diff:
                min_diff = diff
                closest_grade = grade

        return closest_grade

    @staticmethod
    def get_gpa_equivalent(grade_value_id: str) -> float:
        """
        Get the 4.0 GPA equivalent of any grade.

        Args:
            grade_value_id: UUID of the grade value

        Returns:
            GPA equivalent (0.0-4.0)

        Raises:
            ObjectDoesNotExist: If grade value not found
        """
        try:
            grade_value = GradeValue.objects.get(id=grade_value_id)
            return grade_value.gpa_equivalent
        except GradeValue.DoesNotExist as e:
            raise ObjectDoesNotExist(f"Grade value {grade_value_id} not found") from e

    @staticmethod
    def convert_gpa_to_scale(
        gpa_value: float,
        target_scale_id: str
    ) -> GradeValue | None:
        """
        Convert a numeric GPA value to a grade in the target scale.

        Args:
            gpa_value: GPA value (0.0-4.0)
            target_scale_id: UUID of the target grade scale

        Returns:
            Closest GradeValue in target scale, or None if scale not found
        """
        if gpa_value < 0.0 or gpa_value > 4.0:
            raise ValidationError("GPA value must be between 0.0 and 4.0")

        try:
            target_scale = GradeScale.objects.prefetch_related('grade_values').get(
                id=target_scale_id
            )
        except GradeScale.DoesNotExist as e:
            raise ObjectDoesNotExist(f"Grade scale {target_scale_id} not found") from e

        target_grades = target_scale.grade_values.all().order_by('gpa_equivalent')

        if not target_grades:
            return None

        # Find closest match
        closest_grade = None
        min_diff = float('inf')

        for grade in target_grades:
            diff = abs(grade.gpa_equivalent - gpa_value)
            if diff < min_diff:
                min_diff = diff
                closest_grade = grade

        return closest_grade

    @staticmethod
    def get_available_translations(grade_value_id: str) -> list[dict[str, Any]]:
        """
        Get all available translations for a grade value.

        Args:
            grade_value_id: UUID of the grade value

        Returns:
            List of dictionaries with translation information
        """
        try:
            grade_value = GradeValue.objects.select_related('grade_scale').get(
                id=grade_value_id
            )
        except GradeValue.DoesNotExist as e:
            raise ObjectDoesNotExist(f"Grade value {grade_value_id} not found") from e

        translations = []

        # Get direct translations
        direct_trans = GradeTranslation.objects.filter(
            source_grade=grade_value
        ).select_related('target_grade', 'target_grade__grade_scale')

        for trans in direct_trans:
            translations.append({
                'target_scale': trans.target_grade.grade_scale.name,
                'target_scale_code': trans.target_grade.grade_scale.code,
                'target_grade': trans.target_grade.label,
                'target_gpa': trans.target_grade.gpa_equivalent,
                'method': 'direct',
                'confidence': trans.confidence
            })

        return translations

    @staticmethod
    def suggest_translation(
        source_grade_id: str,
        target_grade_id: str,
        notes: str = "",
        user=None
    ) -> GradeTranslation:
        """
        Create a suggested translation mapping between two grades.

        Args:
            source_grade_id: UUID of source grade
            target_grade_id: UUID of target grade
            notes: Optional notes about the translation
            user: User creating the translation

        Returns:
            Created GradeTranslation object

        Raises:
            ValidationError: If translation is invalid
        """
        try:
            source_grade = GradeValue.objects.select_related('grade_scale').get(
                id=source_grade_id
            )
            target_grade = GradeValue.objects.select_related('grade_scale').get(
                id=target_grade_id
            )
        except GradeValue.DoesNotExist as e:
            raise ObjectDoesNotExist(str(e)) from e

        # Validate that grades are from different scales
        if source_grade.grade_scale == target_grade.grade_scale:
            raise ValidationError(
                "Source and target grades must be from different scales"
            )

        # Calculate confidence based on GPA difference
        gpa_diff = abs(source_grade.gpa_equivalent - target_grade.gpa_equivalent)
        confidence = max(0.0, 1.0 - (gpa_diff / 4.0))  # Scale 0-1

        translation, created = GradeTranslation.objects.get_or_create(
            source_grade=source_grade,
            target_grade=target_grade,
            defaults={
                'confidence': confidence,
                'notes': notes,
                'created_by': user
            }
        )

        if not created:
            # Update existing translation
            translation.confidence = confidence
            translation.notes = notes
            if user:
                translation.created_by = user
            translation.save()

        return translation

    @staticmethod
    def check_eligibility_with_translation(
        student_gpa: float,
        student_scale_id: str,
        required_gpa: float,
        required_scale_id: str
    ) -> dict[str, Any]:
        """
        Check if student's grade meets program requirement with translation.

        Args:
            student_gpa: Student's numeric grade in their scale
            student_scale_id: UUID of student's grade scale
            required_gpa: Required numeric grade
            required_scale_id: UUID of required grade scale

        Returns:
            Dictionary with eligibility result and details
        """
        try:
            student_scale = GradeScale.objects.get(id=student_scale_id)
            required_scale = GradeScale.objects.get(id=required_scale_id)
        except GradeScale.DoesNotExist as e:
            raise ObjectDoesNotExist(str(e)) from e

        # Find student's grade value
        student_grade = GradeValue.objects.filter(
            grade_scale=student_scale,
            numeric_value=student_gpa
        ).first()

        if not student_grade:
            # Try to find closest grade value
            student_grade = GradeTranslationService._find_closest_grade(
                student_gpa, student_scale
            )

        if not student_grade:
            return {
                'eligible': False,
                'reason': 'Student grade not found in grade scale',
                'student_gpa_equivalent': None,
                'required_gpa_equivalent': None
            }

        # Find required grade value
        required_grade = GradeValue.objects.filter(
            grade_scale=required_scale,
            numeric_value=required_gpa
        ).first()

        if not required_grade:
            required_grade = GradeTranslationService._find_closest_grade(
                required_gpa, required_scale
            )

        if not required_grade:
            return {
                'eligible': False,
                'reason': 'Required grade not found in grade scale',
                'student_gpa_equivalent': student_grade.gpa_equivalent,
                'required_gpa_equivalent': None
            }

        # Compare using GPA equivalents
        student_gpa_equiv = student_grade.gpa_equivalent
        required_gpa_equiv = required_grade.gpa_equivalent

        eligible = student_gpa_equiv >= required_gpa_equiv

        return {
            'eligible': eligible,
            'student_grade': student_grade.label,
            'student_gpa_equivalent': student_gpa_equiv,
            'required_grade': required_grade.label,
            'required_gpa_equivalent': required_gpa_equiv,
            'reason': 'Meets requirement' if eligible else 'Does not meet requirement'
        }

    @staticmethod
    def _find_closest_grade(
        numeric_value: float,
        grade_scale: GradeScale
    ) -> GradeValue | None:
        """Find the closest grade value in a scale."""
        grades = grade_scale.grade_values.all()

        if not grades:
            return None

        closest_grade = None
        min_diff = float('inf')

        for grade in grades:
            diff = abs(grade.numeric_value - numeric_value)
            if diff < min_diff:
                min_diff = diff
                closest_grade = grade

        return closest_grade

    @staticmethod
    def bulk_create_translations(
        source_scale_id: str,
        target_scale_id: str,
        mapping: dict[str, str],
        user=None
    ) -> list[GradeTranslation]:
        """
        Create multiple translations at once.

        Args:
            source_scale_id: UUID of source grade scale
            target_scale_id: UUID of target grade scale
            mapping: Dict mapping source labels to target labels
            user: User creating the translations

        Returns:
            List of created GradeTranslation objects
        """
        try:
            source_scale = GradeScale.objects.prefetch_related('grade_values').get(
                id=source_scale_id
            )
            target_scale = GradeScale.objects.prefetch_related('grade_values').get(
                id=target_scale_id
            )
        except GradeScale.DoesNotExist as e:
            raise ObjectDoesNotExist(str(e)) from e

        translations = []

        for source_label, target_label in mapping.items():
            try:
                source_grade = source_scale.grade_values.get(label=source_label)
                target_grade = target_scale.grade_values.get(label=target_label)

                translation = GradeTranslationService.suggest_translation(
                    str(source_grade.id),
                    str(target_grade.id),
                    notes=f"Bulk created from {source_scale.code} to {target_scale.code}",
                    user=user
                )
                translations.append(translation)
            except GradeValue.DoesNotExist:
                continue  # Skip if grade not found

        return translations

