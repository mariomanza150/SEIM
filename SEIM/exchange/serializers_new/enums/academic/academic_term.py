"""
Academic Term serializers for the exchange application.

Handles serialization for academic term definitions and management.
"""

from rest_framework import serializers
from ....models import AcademicTerm
from ...base import TimestampedModelSerializer


class AcademicTermSerializer(TimestampedModelSerializer):
    """
    Serializer for AcademicTerm model.
    """
    
    season_display = serializers.CharField(source='get_season_display', read_only=True)
    duration_days = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    is_future = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicTerm
        fields = '__all__'
    
    def get_duration_days(self, obj):
        """Calculate duration in days."""
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None
    
    def get_is_current(self, obj):
        """Check if this is the current academic term."""
        from django.utils import timezone
        today = timezone.now().date()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False
    
    def get_is_future(self, obj):
        """Check if this is a future academic term."""
        from django.utils import timezone
        today = timezone.now().date()
        if obj.start_date:
            return obj.start_date > today
        return False
    
    def validate(self, attrs):
        """Validate academic term dates."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError("End date must be after start date")
            
            # Check for overlapping terms
            overlapping = AcademicTerm.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise serializers.ValidationError("Academic term dates overlap with existing term")
        
        return attrs


class AcademicTermListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing academic terms.
    """
    
    season_display = serializers.CharField(source='get_season_display', read_only=True)
    is_current = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicTerm
        fields = [
            'id', 'name', 'season', 'season_display', 'start_date', 
            'end_date', 'is_current', 'duration_display'
        ]
    
    def get_is_current(self, obj):
        """Check if this is the current academic term."""
        from django.utils import timezone
        today = timezone.now().date()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False
    
    def get_duration_display(self, obj):
        """Get formatted duration display."""
        if obj.start_date and obj.end_date:
            days = (obj.end_date - obj.start_date).days
            weeks = days // 7
            return f"{weeks} weeks ({days} days)"
        return "Duration not set"


class AcademicTermCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating academic terms.
    """
    
    class Meta:
        model = AcademicTerm
        fields = ['name', 'season', 'start_date', 'end_date']
    
    def validate(self, attrs):
        """Validate new academic term."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError("End date must be after start date")
            
            # Check for overlapping terms
            overlapping = AcademicTerm.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if overlapping.exists():
                overlapping_names = list(overlapping.values_list('name', flat=True))
                raise serializers.ValidationError(
                    f"Academic term dates overlap with existing terms: {', '.join(overlapping_names)}"
                )
        
        return attrs


class CurrentAcademicTermSerializer(serializers.Serializer):
    """
    Serializer for getting current academic term information.
    """
    
    def to_representation(self, instance):
        """Return current academic term data."""
        from django.utils import timezone
        
        today = timezone.now().date()
        current_term = AcademicTerm.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        if current_term:
            return AcademicTermSerializer(current_term).data
        
        # If no current term, return the next upcoming term
        next_term = AcademicTerm.objects.filter(
            start_date__gt=today
        ).order_by('start_date').first()
        
        if next_term:
            data = AcademicTermSerializer(next_term).data
            data['is_upcoming'] = True
            return data
        
        return None
