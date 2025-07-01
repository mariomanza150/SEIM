"""
Timeline and workflow serializers for the exchange application.

Handles serialization for timeline events and workflow logging.
"""

from rest_framework import serializers
from ...models import Timeline, WorkflowLog
from ..base import TimestampedModelSerializer, UserSerializer


class TimelineSerializer(TimestampedModelSerializer):
    """
    Serializer for Timeline model.
    """
    
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    actor = UserSerializer(read_only=True)
    related_document = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Computed fields
    is_status_change = serializers.BooleanField(read_only=True)
    formatted_description = serializers.SerializerMethodField()
    event_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Timeline
        fields = '__all__'
        read_only_fields = ['id', 'exchange', 'timestamp']
    
    def get_formatted_description(self, obj):
        """Get formatted description with additional context."""
        description = obj.description
        
        # Add context for status changes
        if obj.is_status_change():
            if obj.previous_value and obj.new_value:
                description += f" (from {obj.previous_value} to {obj.new_value})"
        
        # Add actor information if available
        if obj.actor:
            actor_name = obj.actor.get_full_name() or obj.actor.username
            description += f" by {actor_name}"
        
        return description
    
    def get_event_class(self, obj):
        """Get CSS class for event display based on event type."""
        event_classes = {
            'STATUS_CHANGE': 'primary',
            'DOCUMENT_UPLOAD': 'info',
            'DOCUMENT_APPROVED': 'success',
            'DOCUMENT_REJECTED': 'danger',
            'REVIEW_ADDED': 'warning',
            'COMMENT_ADDED': 'secondary',
            'REMINDER_SENT': 'light',
            'DEADLINE_CHANGED': 'warning',
            'APPLICATION_EDITED': 'info',
            'ASSIGNMENT_CHANGED': 'info',
            'COURSE_ADDED': 'success',
            'COURSE_APPROVED': 'success',
            'GRADE_ADDED': 'primary',
            'GRADE_TRANSFERRED': 'success',
            'MILESTONE': 'primary',
            'OTHER': 'secondary'
        }
        return event_classes.get(obj.event_type, 'secondary')


class TimelineListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing timeline events.
    """
    
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    actor_name = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    event_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Timeline
        fields = [
            'id', 'event_type', 'event_type_display', 'short_description',
            'timestamp', 'actor_name', 'event_class'
        ]
    
    def get_actor_name(self, obj):
        """Get actor's display name."""
        if obj.actor:
            return obj.actor.get_full_name() or obj.actor.username
        return None
    
    def get_short_description(self, obj):
        """Get shortened description for list view."""
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    
    def get_event_class(self, obj):
        """Get CSS class for event display."""
        # Reuse logic from TimelineSerializer
        timeline_serializer = TimelineSerializer()
        return timeline_serializer.get_event_class(obj)


class TimelineCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating timeline events.
    """
    
    class Meta:
        model = Timeline
        fields = [
            'event_type', 'description', 'previous_value', 'new_value',
            'related_document'
        ]
    
    def create(self, validated_data):
        """Create timeline event with context data."""
        validated_data['exchange'] = self.context['exchange']
        validated_data['actor'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_event_type(self, value):
        """Validate event type is allowed."""
        # You could add specific validation here based on user permissions
        # For example, only certain users can create certain event types
        return value


class WorkflowLogSerializer(TimestampedModelSerializer):
    """
    Serializer for WorkflowLog model.
    """
    
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    transition_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowLog
        fields = '__all__'
        read_only_fields = ['id', 'exchange', 'user', 'timestamp']
    
    def get_transition_display(self, obj):
        """Get formatted transition display."""
        return f"{obj.from_status} → {obj.to_status}"


class WorkflowLogListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing workflow logs.
    """
    
    user_name = serializers.SerializerMethodField()
    transition_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowLog
        fields = [
            'id', 'from_status', 'to_status', 'transition_display',
            'user_name', 'comment', 'timestamp'
        ]
    
    def get_user_name(self, obj):
        """Get user's display name."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None
    
    def get_transition_display(self, obj):
        """Get formatted transition display."""
        return f"{obj.from_status} → {obj.to_status}"


class WorkflowLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating workflow logs.
    """
    
    class Meta:
        model = WorkflowLog
        fields = ['from_status', 'to_status', 'comment']
    
    def create(self, validated_data):
        """Create workflow log with context data."""
        validated_data['exchange'] = self.context['exchange']
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TimelineBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for creating multiple timeline events at once.
    """
    
    events = serializers.ListField(
        child=TimelineCreateSerializer(),
        min_length=1,
        help_text="List of timeline events to create"
    )
    
    def create(self, validated_data):
        """Create multiple timeline events."""
        events_data = validated_data['events']
        exchange = self.context['exchange']
        user = self.context['request'].user
        
        timeline_events = []
        for event_data in events_data:
            event_data['exchange'] = exchange
            event_data['actor'] = user
            timeline_events.append(Timeline(**event_data))
        
        return Timeline.objects.bulk_create(timeline_events)


class TimelineFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering timeline events.
    """
    
    event_types = serializers.MultipleChoiceField(
        choices=Timeline.EVENT_TYPES,
        required=False,
        help_text="Filter by event types"
    )
    date_from = serializers.DateTimeField(
        required=False,
        help_text="Filter events from this date"
    )
    date_to = serializers.DateTimeField(
        required=False,
        help_text="Filter events to this date"
    )
    actor_id = serializers.IntegerField(
        required=False,
        help_text="Filter by actor user ID"
    )
    
    def validate(self, attrs):
        """Validate date range."""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from must be before date_to")
        
        return attrs


class WorkflowStatisticsSerializer(serializers.Serializer):
    """
    Serializer for workflow statistics.
    """
    
    total_transitions = serializers.IntegerField(read_only=True)
    transitions_by_status = serializers.DictField(read_only=True)
    avg_time_in_status = serializers.DictField(read_only=True)
    most_active_users = serializers.ListField(read_only=True)
    recent_activity = serializers.ListField(read_only=True)
