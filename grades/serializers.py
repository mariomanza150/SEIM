"""Serializers for grade translation API."""
from rest_framework import serializers

from .models import GradeScale, GradeTranslation, GradeValue


class GradeValueSerializer(serializers.ModelSerializer):
    """Serializer for grade values."""
    grade_scale_name = serializers.CharField(source='grade_scale.name', read_only=True)
    grade_scale_code = serializers.CharField(source='grade_scale.code', read_only=True)

    class Meta:
        model = GradeValue
        fields = [
            'id', 'grade_scale', 'grade_scale_name', 'grade_scale_code',
            'label', 'numeric_value', 'gpa_equivalent',
            'min_percentage', 'max_percentage', 'description',
            'order', 'is_passing', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GradeScaleSerializer(serializers.ModelSerializer):
    """Serializer for grade scales."""
    grade_values = GradeValueSerializer(many=True, read_only=True)
    grade_count = serializers.IntegerField(source='grade_values.count', read_only=True)

    class Meta:
        model = GradeScale
        fields = [
            'id', 'name', 'code', 'description', 'country',
            'min_value', 'max_value', 'passing_value',
            'is_active', 'is_reverse_scale', 'grade_values', 'grade_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GradeScaleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing grade scales."""
    grade_count = serializers.SerializerMethodField()

    class Meta:
        model = GradeScale
        fields = [
            'id', 'name', 'code', 'country', 'is_active',
            'min_value', 'max_value', 'grade_count'
        ]

    def get_grade_count(self, obj):
        """Get the count of grade values."""
        return obj.grade_values.count()


class GradeTranslationSerializer(serializers.ModelSerializer):
    """Serializer for grade translations."""
    source_grade_label = serializers.CharField(source='source_grade.label', read_only=True)
    source_scale_code = serializers.CharField(
        source='source_grade.grade_scale.code', read_only=True
    )
    target_grade_label = serializers.CharField(source='target_grade.label', read_only=True)
    target_scale_code = serializers.CharField(
        source='target_grade.grade_scale.code', read_only=True
    )
    gpa_difference = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True, allow_null=True
    )

    class Meta:
        model = GradeTranslation
        fields = [
            'id', 'source_grade', 'source_grade_label', 'source_scale_code',
            'target_grade', 'target_grade_label', 'target_scale_code',
            'confidence', 'notes', 'gpa_difference',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_gpa_difference(self, obj):
        """Calculate GPA difference between source and target."""
        return abs(obj.source_grade.gpa_equivalent - obj.target_grade.gpa_equivalent)


class GradeTranslationRequestSerializer(serializers.Serializer):
    """Serializer for grade translation requests."""
    source_grade_value_id = serializers.UUIDField(required=True)
    target_scale_id = serializers.UUIDField(required=True)
    fallback_to_gpa = serializers.BooleanField(default=True)


class GradeTranslationResponseSerializer(serializers.Serializer):
    """Serializer for grade translation responses."""
    source_grade = GradeValueSerializer()
    target_grade = GradeValueSerializer(allow_null=True)
    translation_method = serializers.CharField()
    confidence = serializers.FloatField(allow_null=True)


class GPAConversionRequestSerializer(serializers.Serializer):
    """Serializer for GPA conversion requests."""
    gpa_value = serializers.FloatField(min_value=0.0, max_value=4.0)
    target_scale_id = serializers.UUIDField()


class EligibilityCheckRequestSerializer(serializers.Serializer):
    """Serializer for eligibility check with translation."""
    student_gpa = serializers.FloatField()
    student_scale_id = serializers.UUIDField()
    required_gpa = serializers.FloatField()
    required_scale_id = serializers.UUIDField()


class EligibilityCheckResponseSerializer(serializers.Serializer):
    """Serializer for eligibility check response."""
    eligible = serializers.BooleanField()
    student_grade = serializers.CharField(allow_null=True)
    student_gpa_equivalent = serializers.FloatField(allow_null=True)
    required_grade = serializers.CharField(allow_null=True)
    required_gpa_equivalent = serializers.FloatField(allow_null=True)
    reason = serializers.CharField()


class BulkTranslationRequestSerializer(serializers.Serializer):
    """Serializer for bulk translation creation."""
    source_scale_id = serializers.UUIDField()
    target_scale_id = serializers.UUIDField()
    mapping = serializers.DictField(
        child=serializers.CharField(),
        help_text="Dictionary mapping source labels to target labels"
    )

