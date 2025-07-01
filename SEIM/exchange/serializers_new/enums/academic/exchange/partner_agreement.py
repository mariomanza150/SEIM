"""
Partner Agreement serializers for the exchange application.

Handles serialization for partner agreements between universities.
"""

from rest_framework import serializers
from .....models import PartnerAgreement
from ....base import TimestampedModelSerializer


class PartnerAgreementSerializer(TimestampedModelSerializer):
    """
    Serializer for PartnerAgreement model.
    """
    
    home_university = serializers.StringRelatedField(read_only=True)
    partner_university = serializers.StringRelatedField(read_only=True)
    program = serializers.StringRelatedField(read_only=True)
    home_university_id = serializers.IntegerField(write_only=True, required=False)
    partner_university_id = serializers.IntegerField(write_only=True, required=False)
    program_id = serializers.IntegerField(write_only=True, required=False)
    
    # Computed fields
    duration_days = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    agreement_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerAgreement
        fields = '__all__'
    
    def get_duration_days(self, obj):
        """Calculate agreement duration in days."""
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None
    
    def get_is_current(self, obj):
        """Check if agreement is currently active."""
        if not obj.active:
            return False
        
        from django.utils import timezone
        today = timezone.now().date()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False
    
    def get_is_expired(self, obj):
        """Check if agreement has expired."""
        from django.utils import timezone
        today = timezone.now().date()
        if obj.end_date:
            return today > obj.end_date
        return False
    
    def get_agreement_display(self, obj):
        """Get formatted agreement display."""
        return str(obj)
    
    def validate(self, attrs):
        """Validate partner agreement data."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        home_university_id = attrs.get('home_university_id')
        partner_university_id = attrs.get('partner_university_id')
        quota_limit = attrs.get('quota_limit')
        
        # Validate dates
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        
        # Validate universities are different
        if home_university_id and partner_university_id and home_university_id == partner_university_id:
            raise serializers.ValidationError("Home and partner universities must be different")
        
        # Validate quota limit
        if quota_limit and quota_limit <= 0:
            raise serializers.ValidationError("Quota limit must be greater than zero")
        
        return attrs


class PartnerAgreementListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing partner agreements.
    """
    
    home_university_name = serializers.CharField(source='home_university.name', read_only=True)
    partner_university_name = serializers.CharField(source='partner_university.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    is_current = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = PartnerAgreement
        fields = [
            'id', 'home_university_name', 'partner_university_name',
            'program_name', 'program_code', 'start_date', 'end_date',
            'active', 'is_current', 'is_expired', 'quota_limit'
        ]
    
    def get_is_current(self, obj):
        """Check if agreement is currently active."""
        if not obj.active:
            return False
        
        from django.utils import timezone
        today = timezone.now().date()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False
    
    def get_is_expired(self, obj):
        """Check if agreement has expired."""
        from django.utils import timezone
        today = timezone.now().date()
        if obj.end_date:
            return today > obj.end_date
        return False


class PartnerAgreementCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating partner agreements.
    """
    
    home_university_id = serializers.IntegerField()
    partner_university_id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    
    class Meta:
        model = PartnerAgreement
        fields = [
            'home_university_id', 'partner_university_id', 'program_id',
            'start_date', 'end_date', 'active', 'quota_limit'
        ]
    
    def validate(self, attrs):
        """Validate new partner agreement."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        home_university_id = attrs.get('home_university_id')
        partner_university_id = attrs.get('partner_university_id')
        
        # Validate dates
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        
        # Validate universities are different
        if home_university_id == partner_university_id:
            raise serializers.ValidationError("Home and partner universities must be different")
        
        return attrs
