"""
Application Status serializers for the exchange application.

Handles serialization for application status definitions and management.
"""

from rest_framework import serializers
from ...models import ApplicationStatus
from ..base import TimestampedModelSerializer


class ApplicationStatusSerializer(TimestampedModelSerializer):
    """
    Serializer for ApplicationStatus model.
    """
    
    is_terminal = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ApplicationStatus
        fields = '__all__'
    
    def validate_color_code(self, value):
        """Validate hex color code format."""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError(
                "Color code must be a valid hex color (e.g., #FF0000)"
            )
        return value
    
    def validate_name(self, value):
        """Validate status name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Status name cannot be empty")
        
        # Check for duplicate names (excluding current instance if updating)
        qs = ApplicationStatus.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Status name must be unique")
        
        return value.strip()


class ApplicationStatusListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing application statuses.
    """
    
    is_terminal = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ApplicationStatus
        fields = ['id', 'name', 'color_code', 'is_terminal']


class ApplicationStatusCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating application statuses.
    """
    
    class Meta:
        model = ApplicationStatus
        fields = ['name', 'color_code']
    
    def validate_color_code(self, value):
        """Validate hex color code format."""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError(
                "Color code must be a valid hex color (e.g., #FF0000)"
            )
        return value


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating application statuses.
    """
    
    class Meta:
        model = ApplicationStatus
        fields = ['name', 'color_code']
    
    def validate_name(self, value):
        """Validate status name for uniqueness."""
        if not value or not value.strip():
            raise serializers.ValidationError("Status name cannot be empty")
        
        # Check for duplicate names excluding current instance
        qs = ApplicationStatus.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Status name must be unique")
        
        return value.strip()
    
    def validate_color_code(self, value):
        """Validate hex color code format."""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError(
                "Color code must be a valid hex color (e.g., #FF0000)"
            )
        return value


class ApplicationStatusBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on application statuses.
    """
    
    statuses = serializers.ListField(
        child=ApplicationStatusCreateSerializer(),
        min_length=1,
        help_text="List of statuses to create"
    )
    
    def create(self, validated_data):
        """Create multiple statuses."""
        statuses_data = validated_data['statuses']
        
        # Check for duplicate names in the batch
        names = [status['name'] for status in statuses_data]
        if len(names) != len(set(name.lower() for name in names)):
            raise serializers.ValidationError("Duplicate status names in batch")
        
        # Check for existing names
        existing_names = ApplicationStatus.objects.filter(
            name__iexact__in=names
        ).values_list('name', flat=True)
        
        if existing_names:
            raise serializers.ValidationError(
                f"Status names already exist: {list(existing_names)}"
            )
        
        # Create statuses
        statuses = []
        for status_data in statuses_data:
            status = ApplicationStatus(**status_data)
            statuses.append(status)
        
        return ApplicationStatus.objects.bulk_create(statuses)


class ApplicationStatusUsageSerializer(serializers.Serializer):
    """
    Serializer for application status usage statistics.
    """
    
    status_id = serializers.IntegerField(read_only=True)
    status_name = serializers.CharField(read_only=True)
    color_code = serializers.CharField(read_only=True)
    usage_count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    is_terminal = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)


class ApplicationStatusValidationSerializer(serializers.Serializer):
    """
    Serializer for validating status changes and transitions.
    """
    
    from_status_id = serializers.IntegerField()
    to_status_id = serializers.IntegerField()
    
    def validate_from_status_id(self, value):
        """Validate from status exists."""
        try:
            ApplicationStatus.objects.get(id=value)
        except ApplicationStatus.DoesNotExist:
            raise serializers.ValidationError("Invalid from status ID")
        return value
    
    def validate_to_status_id(self, value):
        """Validate to status exists."""
        try:
            ApplicationStatus.objects.get(id=value)
        except ApplicationStatus.DoesNotExist:
            raise serializers.ValidationError("Invalid to status ID")
        return value
    
    def validate(self, attrs):
        """Validate status transition is allowed."""
        from_status_id = attrs['from_status_id']
        to_status_id = attrs['to_status_id']
        
        if from_status_id == to_status_id:
            raise serializers.ValidationError("From and to status cannot be the same")
        
        # Get status objects
        from_status = ApplicationStatus.objects.get(id=from_status_id)
        to_status = ApplicationStatus.objects.get(id=to_status_id)
        
        # Check if transition from terminal status is allowed
        if from_status.is_terminal():
            raise serializers.ValidationError(
                f"Cannot transition from terminal status '{from_status.name}'"
            )
        
        # Add additional business logic for valid transitions here
        # For example, certain statuses can only transition to specific other statuses
        
        return attrs
