"""
Program Type serializers for the exchange application.

Handles serialization for exchange program type definitions.
"""

from rest_framework import serializers
from .....models import ProgramType
from ....base import TimestampedModelSerializer


class ProgramTypeSerializer(TimestampedModelSerializer):
    """
    Serializer for ProgramType model.
    """
    
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramType
        fields = '__all__'
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using this type."""
        if hasattr(obj, 'exchangeprogram_set'):
            return obj.exchangeprogram_set.count()
        return 0
    
    def validate_name(self, value):
        """Validate program type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Program type name cannot be empty")
        
        # Check for duplicate names (excluding current instance if updating)
        qs = ProgramType.objects.filter(name__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("Program type name must be unique")
        
        return value.strip()


class ProgramTypeListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing program types.
    """
    
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramType
        fields = ['id', 'name', 'programs_count']
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using this type."""
        if hasattr(obj, 'exchangeprogram_set'):
            return obj.exchangeprogram_set.count()
        return 0


class ProgramTypeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating program types.
    """
    
    class Meta:
        model = ProgramType
        fields = ['name']
    
    def validate_name(self, value):
        """Validate program type name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Program type name cannot be empty")
        
        # Check for duplicate names
        if ProgramType.objects.filter(name__iexact=value.strip()).exists():
            raise serializers.ValidationError("Program type name must be unique")
        
        return value.strip()


class ProgramTypeBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk program type operations.
    """
    
    program_types = serializers.ListField(
        child=ProgramTypeCreateSerializer(),
        min_length=1,
        help_text="List of program types to create"
    )
    
    def create(self, validated_data):
        """Create multiple program types."""
        types_data = validated_data['program_types']
        
        # Check for duplicate names in the batch
        names = [pt['name'] for pt in types_data]
        if len(names) != len(set(name.lower() for name in names)):
            raise serializers.ValidationError("Duplicate program type names in batch")
        
        # Check for existing names
        existing_names = ProgramType.objects.filter(
            name__iexact__in=names
        ).values_list('name', flat=True)
        
        if existing_names:
            raise serializers.ValidationError(
                f"Program type names already exist: {list(existing_names)}"
            )
        
        # Create program types
        program_types = []
        for pt_data in types_data:
            pt = ProgramType(**pt_data)
            program_types.append(pt)
        
        return ProgramType.objects.bulk_create(program_types)


class ProgramTypeUsageSerializer(serializers.Serializer):
    """
    Serializer for program type usage statistics.
    """
    
    program_type_id = serializers.IntegerField(read_only=True)
    program_type_name = serializers.CharField(read_only=True)
    programs_count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)
