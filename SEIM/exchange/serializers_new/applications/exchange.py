"""
Exchange application serializers.

Handles serialization for the main Exchange model and related operations.
"""

from rest_framework import serializers
from django.db import transaction
from ...models import Exchange
from ..base import TimestampedModelSerializer, UserSerializer


class ExchangeListSerializer(TimestampedModelSerializer):
    """
    Simplified serializer for listing exchanges.
    """
    
    student = UserSerializer(read_only=True)
    exchange_program = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_class = serializers.CharField(source='get_status_display_class', read_only=True)
    progress_percentage = serializers.IntegerField(source='get_progress_percentage', read_only=True)
    document_count = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    can_be_edited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exchange
        fields = [
            'id', 'student', 'exchange_program', 'host_university', 
            'destination_country', 'start_date', 'end_date', 'status',
            'status_display', 'status_class', 'progress_percentage',
            'submission_date', 'document_count', 'course_count',
            'can_be_edited', 'created_at', 'updated_at'
        ]
    
    def get_document_count(self, obj):
        """Get count of uploaded documents."""
        return obj.documents.filter(is_deleted=False).count() if hasattr(obj, 'documents') else 0
    
    def get_course_count(self, obj):
        """Get count of courses."""
        return obj.courses.count() if hasattr(obj, 'courses') else 0


class ExchangeDetailSerializer(TimestampedModelSerializer):
    """
    Detailed serializer for exchange applications with all information.
    """
    
    student = UserSerializer(read_only=True)
    exchange_program = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_class = serializers.CharField(source='get_status_display_class', read_only=True)
    progress_percentage = serializers.IntegerField(source='get_progress_percentage', read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    
    # Related data
    documents = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    timeline_events = serializers.SerializerMethodField()
    
    # Validation and status checks
    can_submit = serializers.SerializerMethodField()
    has_required_documents = serializers.SerializerMethodField()
    missing_documents = serializers.SerializerMethodField()
    available_transitions = serializers.SerializerMethodField()
    can_be_edited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exchange
        fields = '__all__'
        read_only_fields = [
            'id', 'submission_date', 'review_date', 'decision_date', 
            'completion_date', 'reviewed_by', 'approved_by', 'created_at', 'updated_at'
        ]
    
    def get_documents(self, obj):
        """Get related documents (avoid circular import)."""
        if hasattr(obj, 'documents'):
            from .document import DocumentSerializer
            return DocumentSerializer(
                obj.documents.filter(is_deleted=False), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def get_courses(self, obj):
        """Get related courses (avoid circular import)."""
        if hasattr(obj, 'courses'):
            from .course import CourseSerializer
            return CourseSerializer(
                obj.courses.all(), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def get_comments(self, obj):
        """Get related comments (avoid circular import)."""
        if hasattr(obj, 'comments'):
            from .comment import CommentSerializer
            return CommentSerializer(
                obj.comments.all(), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def get_timeline_events(self, obj):
        """Get timeline events."""
        return obj.get_timeline_events() if hasattr(obj, 'get_timeline_events') else []
    
    def get_can_submit(self, obj):
        """Check if exchange can be submitted."""
        return obj.status == 'DRAFT' and obj.has_required_documents()
    
    def get_has_required_documents(self, obj):
        """Check if all required documents are uploaded."""
        return obj.has_required_documents() if hasattr(obj, 'has_required_documents') else False
    
    def get_missing_documents(self, obj):
        """Get list of missing required documents."""
        return obj.get_missing_documents() if hasattr(obj, 'get_missing_documents') else []
    
    def get_available_transitions(self, obj):
        """Get available status transitions."""
        return obj.get_available_transitions() if hasattr(obj, 'get_available_transitions') else []


class ExchangeSerializer(TimestampedModelSerializer):
    """
    Standard serializer for Exchange model with common fields.
    """
    
    student = UserSerializer(read_only=True)
    exchange_program_id = serializers.IntegerField(write_only=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_edited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exchange
        fields = [
            'id', 'student', 'exchange_program', 'exchange_program_id',
            'current_university', 'host_university', 'destination_country',
            'current_program', 'current_year', 'gpa', 'degree', 'major',
            'program', 'academic_year', 'current_semester', 'start_date',
            'end_date', 'motivation_letter', 'study_goals', 'special_requirements',
            'referral_source', 'status', 'status_display', 'language_proficiencies',
            'emergency_contact_name', 'emergency_contact_phone', 
            'emergency_contact_relationship', 'notes', 'rejection_reason',
            'can_be_edited', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student', 'submission_date', 'review_date', 'decision_date',
            'completion_date', 'reviewed_by', 'approved_by', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create exchange with current user as student."""
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_start_date(self, value):
        """Validate start date."""
        if value and self.instance and self.instance.end_date:
            if value >= self.instance.end_date:
                raise serializers.ValidationError("Start date must be before end date.")
        return value
    
    def validate_end_date(self, value):
        """Validate end date."""
        if value and self.instance and self.instance.start_date:
            if value <= self.instance.start_date:
                raise serializers.ValidationError("End date must be after start date.")
        return value
    
    def validate_gpa(self, value):
        """Validate GPA range."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("GPA must be between 0 and 10.")
        return value


class ExchangeSubmitSerializer(serializers.Serializer):
    """
    Serializer for submitting an exchange application.
    """
    
    confirm = serializers.BooleanField(
        required=True, 
        help_text="Confirm that all information is correct and complete"
    )
    
    def validate_confirm(self, value):
        """Ensure confirmation is provided."""
        if not value:
            raise serializers.ValidationError("You must confirm to submit the application")
        return value
    
    def validate(self, attrs):
        """Validate that the exchange can be submitted."""
        exchange = self.context['exchange']
        
        if exchange.status != 'DRAFT':
            raise serializers.ValidationError("Only draft applications can be submitted")
        
        if not exchange.has_required_documents():
            missing_docs = exchange.get_missing_documents()
            raise serializers.ValidationError(
                f"Cannot submit without required documents: {', '.join(missing_docs)}"
            )
        
        return attrs


class ExchangeStatusTransitionSerializer(serializers.Serializer):
    """
    Serializer for handling status transitions.
    """
    
    action = serializers.ChoiceField(
        choices=['submit', 'start_review', 'approve', 'reject', 'complete', 'cancel'],
        required=True
    )
    comment = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate transition is allowed."""
        exchange = self.context['exchange']
        action = attrs['action']
        
        # Check if transition is available
        available_transitions = exchange.get_available_transitions() if hasattr(exchange, 'get_available_transitions') else []
        available_actions = [t['name'] for t in available_transitions if t.get('available', False)]
        
        if action not in available_actions:
            raise serializers.ValidationError(f"Action '{action}' is not available for current status")
        
        # Require reason for reject and cancel
        if action in ['reject', 'cancel'] and not attrs.get('reason'):
            raise serializers.ValidationError(f"Reason is required for {action} action")
        
        return attrs
