"""
Funding Type serializers for the exchange application.

Handles serialization for funding type definitions and management.
"""

from rest_framework import serializers
from .....models import FundingType
from ....base import TimestampedModelSerializer


class FundingTypeSerializer(TimestampedModelSerializer):
    """
    Serializer for FundingType model.
    """
    
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FundingType
        fields = '__all__'
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using this funding type."""
        if hasattr(obj, 'exchange_programs'):
            return obj.exchange_programs.count()
        return 0
    
    def validate_name(self, value):
        """Validate funding type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Funding type name cannot be empty")
        
        # Check for duplicate names (excluding current instance if updating)
        qs = FundingType.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Funding type name must be unique")
        
        return value.strip()


class FundingTypeListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing funding types.
    """
    
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FundingType
        fields = ['id', 'name', 'description', 'is_recurring', 'programs_count']
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using this funding type."""
        if hasattr(obj, 'exchange_programs'):
            return obj.exchange_programs.count()
        return 0


class FundingTypeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating funding types.
    """
    
    class Meta:
        model = FundingType
        fields = ['name', 'description', 'is_recurring']
    
    def validate_name(self, value):
        """Validate funding type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Funding type name cannot be empty")
        
        # Check for duplicate names
        if FundingType.objects.filter(name__iexact=value.strip()).exists():
            raise serializers.ValidationError("Funding type name must be unique")
        
        return value.strip()


class FundingTypeBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk funding type operations.
    """
    
    funding_types = serializers.ListField(
        child=FundingTypeCreateSerializer(),
        min_length=1,
        help_text="List of funding types to create"
    )
    
    def create(self, validated_data):
        """Create multiple funding types."""
        funding_types_data = validated_data['funding_types']
        
        # Check for duplicate names in the batch
        names = [ft['name'] for ft in funding_types_data]
        if len(names) != len(set(name.lower() for name in names)):
            raise serializers.ValidationError("Duplicate funding type names in batch")
        
        # Check for existing names
        existing_names = FundingType.objects.filter(
            name__iexact__in=names
        ).values_list('name', flat=True)
        
        if existing_names:
            raise serializers.ValidationError(
                f"Funding type names already exist: {list(existing_names)}"
            )
        
        # Create funding types
        funding_types = []
        for ft_data in funding_types_data:
            ft = FundingType(**ft_data)
            funding_types.append(ft)
        
        return FundingType.objects.bulk_create(funding_types)


class FundingTypeUsageSerializer(serializers.Serializer):
    """
    Serializer for funding type usage statistics.
    """
    
    funding_type_id = serializers.IntegerField(read_only=True)
    funding_type_name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    is_recurring = serializers.BooleanField(read_only=True)
    programs_count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)
