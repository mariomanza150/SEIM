"""
Student Profile serializers for the exchange application.

Handles serialization for student profile management.
"""

from rest_framework import serializers
from ....models import StudentProfile
from ...base import TimestampedModelSerializer, UserSerializer
from ..enums.address import CountrySerializer
from ..enums import UniversitySerializer


class StudentProfileSerializer(TimestampedModelSerializer):
    """
    Serializer for StudentProfile model.
    """
    
    user = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    university_id = serializers.IntegerField(write_only=True, required=False)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    profile_completeness = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_profile_completeness(self, obj):
        """Get profile completeness percentage."""
        return obj.get_profile_completeness() if hasattr(obj, 'get_profile_completeness') else 0
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format."""
        if value:
            # Remove common formatting characters
            cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits and common formatting characters")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate date of birth is reasonable."""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            
            today = timezone.now().date()
            min_age = today - timedelta(days=100*365)  # 100 years old
            max_age = today - timedelta(days=13*365)   # 13 years old minimum
            
            if value < min_age or value > max_age:
                raise serializers.ValidationError("Date of birth must be between 13 and 100 years ago")
        
        return value


class StudentProfileListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing student profiles.
    """
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)
    profile_completeness = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user_name', 'username', 'email', 'student_id',
            'university_name', 'institution', 'degree', 'profile_completeness',
            'is_verified', 'created_at'
        ]
    
    def get_profile_completeness(self, obj):
        """Get profile completeness percentage."""
        return obj.get_profile_completeness() if hasattr(obj, 'get_profile_completeness') else 0


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating student profiles.
    """
    
    university_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth', 'gender', 'phone', 'address', 'city', 'country',
            'academic_level', 'university_id', 'institution', 'degree', 'student_id'
        ]
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format."""
        if value:
            cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if not cleaned.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits and formatting characters")
        return value
    
    def create(self, validated_data):
        """Create student profile with user from context."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating student profiles.
    """
    
    university_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth', 'gender', 'phone', 'address', 'city', 'country',
            'academic_level', 'university_id', 'institution', 'degree', 'student_id'
        ]
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value


class StudentProfileVerificationSerializer(serializers.Serializer):
    """
    Serializer for student profile verification.
    """
    
    verified = serializers.BooleanField()
    verification_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate verification data."""
        if not attrs.get('verified') and not attrs.get('verification_notes'):
            raise serializers.ValidationError({
                'verification_notes': 'Notes are required when rejecting verification'
            })
        return attrs


class StudentProfileSearchSerializer(serializers.Serializer):
    """
    Serializer for searching student profiles.
    """
    
    query = serializers.CharField(required=False, help_text="Search by name, email, or student ID")
    university_id = serializers.IntegerField(required=False)
    degree = serializers.CharField(required=False)
    academic_level = serializers.CharField(required=False)
    verified_only = serializers.BooleanField(required=False)
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def filter_queryset(self, queryset):
        """Filter queryset based on search criteria."""
        query = self.validated_data.get('query')
        university_id = self.validated_data.get('university_id')
        degree = self.validated_data.get('degree')
        academic_level = self.validated_data.get('academic_level')
        verified_only = self.validated_data.get('verified_only')
        
        if query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(student_id__icontains=query)
            )
        
        if university_id:
            queryset = queryset.filter(university_id=university_id)
        
        if degree:
            queryset = queryset.filter(degree__icontains=degree)
        
        if academic_level:
            queryset = queryset.filter(academic_level__icontains=academic_level)
        
        if verified_only:
            queryset = queryset.filter(is_verified=True)
        
        return queryset


class StudentProfileStatisticsSerializer(serializers.Serializer):
    """
    Serializer for student profile statistics.
    """
    
    def to_representation(self, instance):
        """Return student profile statistics."""
        from django.db.models import Count, Q
        
        total_students = StudentProfile.objects.count()
        verified_students = StudentProfile.objects.filter(is_verified=True).count()
        
        # Statistics by university
        university_stats = StudentProfile.objects.values(
            'university__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Statistics by degree
        degree_stats = StudentProfile.objects.values(
            'degree'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Profile completeness distribution
        profiles_with_completeness = []
        for profile in StudentProfile.objects.all():
            completeness = profile.get_profile_completeness() if hasattr(profile, 'get_profile_completeness') else 0
            profiles_with_completeness.append(completeness)
        
        # Calculate completeness ranges
        completeness_ranges = {
            '0-25%': len([c for c in profiles_with_completeness if 0 <= c < 25]),
            '25-50%': len([c for c in profiles_with_completeness if 25 <= c < 50]),
            '50-75%': len([c for c in profiles_with_completeness if 50 <= c < 75]),
            '75-100%': len([c for c in profiles_with_completeness if 75 <= c <= 100]),
        }
        
        avg_completeness = sum(profiles_with_completeness) / len(profiles_with_completeness) if profiles_with_completeness else 0
        
        return {
            'total_students': total_students,
            'verified_students': verified_students,
            'verification_rate': round((verified_students / total_students) * 100, 2) if total_students > 0 else 0,
            'top_universities': list(university_stats),
            'top_degrees': list(degree_stats),
            'profile_completeness': {
                'average': round(avg_completeness, 2),
                'distribution': completeness_ranges
            }
        }


class StudentProfileBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk student profile operations.
    """
    
    action = serializers.ChoiceField(
        choices=['verify', 'unverify'],
        help_text="Action to perform on selected profiles"
    )
    profile_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of profile IDs to update"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for the bulk action"
    )
    
    def validate_profile_ids(self, value):
        """Validate that all profile IDs exist."""
        existing_ids = StudentProfile.objects.filter(id__in=value).values_list('id', flat=True)
        invalid_ids = set(value) - set(existing_ids)
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid profile IDs: {list(invalid_ids)}")
        return value
    
    def perform_bulk_action(self):
        """Perform the bulk action on selected profiles."""
        action = self.validated_data['action']
        profile_ids = self.validated_data['profile_ids']
        notes = self.validated_data.get('notes', '')
        
        profiles = StudentProfile.objects.filter(id__in=profile_ids)
        
        if action == 'verify':
            from django.utils import timezone
            profiles.update(is_verified=True, verification_date=timezone.now())
        elif action == 'unverify':
            profiles.update(is_verified=False, verification_date=None)
        
        return {
            'action': action,
            'updated_count': profiles.count(),
            'notes': notes
        }
