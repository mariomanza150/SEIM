"""
Course and Grade serializers for the exchange application.

Handles serialization for course planning, enrollment, and grade recording.
"""

from rest_framework import serializers
from ...models import Course, Grade
from ..base import TimestampedModelSerializer, UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.
    """
    
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by = UserSerializer(read_only=True)
    
    # Status check methods
    is_approved = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_in_progress = serializers.BooleanField(read_only=True)
    is_planned = serializers.BooleanField(read_only=True)
    
    # Computed fields
    total_credits = serializers.SerializerMethodField()
    grade_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['approved_by', 'approved_at']
    
    def get_total_credits(self, obj):
        """Get total credits (home credits if available, otherwise host credits)."""
        return obj.home_credits if obj.home_credits else obj.credits
    
    def get_grade_info(self, obj):
        """Get grade information if available."""
        if hasattr(obj, 'grades') and obj.grades.exists():
            latest_grade = obj.grades.latest('date_received')
            return {
                'host_grade': latest_grade.host_grade,
                'converted_grade': latest_grade.converted_grade,
                'status': latest_grade.status,
                'date_received': latest_grade.date_received
            }
        return None
    
    def validate_credits(self, value):
        """Validate credits are positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Credits must be greater than zero")
        return value
    
    def validate_hours_per_week(self, value):
        """Validate hours per week are positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Hours per week must be greater than zero")
        return value
    
    def validate_home_credits(self, value):
        """Validate home credits are positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Home credits must be greater than zero")
        return value


class CourseListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing courses.
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_credits = serializers.SerializerMethodField()
    has_grade = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'host_university',
            'department', 'credits', 'home_credits', 'total_credits',
            'status', 'status_display', 'has_grade'
        ]
    
    def get_total_credits(self, obj):
        """Get total credits."""
        return obj.home_credits if obj.home_credits else obj.credits
    
    def get_has_grade(self, obj):
        """Check if course has any grades."""
        return hasattr(obj, 'grades') and obj.grades.exists()


class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new courses.
    """
    
    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'host_university', 'department',
            'credits', 'hours_per_week', 'description', 'home_course_code',
            'home_course_name', 'home_credits'
        ]
    
    def create(self, validated_data):
        """Create course with exchange from context."""
        validated_data['exchange'] = self.context['exchange']
        return super().create(validated_data)


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for Grade model.
    """
    
    course = CourseListSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    grade_document = serializers.PrimaryKeyRelatedField(read_only=True)
    grade_document_id = serializers.IntegerField(write_only=True, required=False)
    processed_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ['processed_by', 'date_processed']
    
    def validate_course_id(self, value):
        """Validate that the course exists and belongs to the same exchange."""
        try:
            course = Course.objects.get(id=value)
            # Additional validation could be added here to ensure
            # the course belongs to the current user's exchange
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Invalid course ID")
    
    def validate_date_received(self, value):
        """Validate date received is not in the future."""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Date received cannot be in the future")
        return value


class GradeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new grades.
    """
    
    course_id = serializers.IntegerField()
    
    class Meta:
        model = Grade
        fields = [
            'course_id', 'host_grade', 'host_grade_description',
            'converted_grade', 'date_received', 'notes'
        ]
    
    def create(self, validated_data):
        """Create grade with course validation."""
        course_id = validated_data.pop('course_id')
        try:
            course = Course.objects.get(id=course_id)
            validated_data['course'] = course
            return super().create(validated_data)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Invalid course ID")


class GradeTransferSerializer(serializers.Serializer):
    """
    Serializer for transferring grades to home university.
    """
    
    confirm = serializers.BooleanField(
        required=True,
        help_text="Confirm transfer to home university"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Additional notes for the transfer"
    )
    
    def validate_confirm(self, value):
        """Ensure confirmation is provided."""
        if not value:
            raise serializers.ValidationError("Confirmation is required for grade transfer")
        return value


class CourseBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk course operations.
    """
    
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of course IDs to update"
    )
    action = serializers.ChoiceField(
        choices=['approve', 'enroll', 'complete', 'drop'],
        help_text="Action to perform on selected courses"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for the bulk action"
    )
    
    def validate_course_ids(self, value):
        """Validate that all course IDs exist."""
        existing_ids = Course.objects.filter(id__in=value).values_list('id', flat=True)
        invalid_ids = set(value) - set(existing_ids)
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid course IDs: {list(invalid_ids)}")
        return value
