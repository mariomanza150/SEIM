"""
Program Requirements serializers for the exchange application.

Handles serialization for exchange program requirements.
"""

from rest_framework import serializers
from .....models import ProgramRequirements
from ....base import TimestampedModelSerializer


class ProgramRequirementsSerializer(TimestampedModelSerializer):
    """
    Serializer for ProgramRequirements model.
    """
    
    duration_unit_display = serializers.CharField(source='get_duration_unit_display', read_only=True)
    duration_range = serializers.SerializerMethodField()
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramRequirements
        fields = '__all__'
    
    def get_duration_range(self, obj):
        """Get formatted duration range."""
        if obj.min_duration == obj.max_duration:
            return f"{obj.min_duration} {obj.get_duration_unit_display()}"
        return f"{obj.min_duration}-{obj.max_duration} {obj.get_duration_unit_display()}"
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using these requirements."""
        if hasattr(obj, 'exchangeprogram_set'):
            return obj.exchangeprogram_set.count()
        return 0
    
    def validate(self, attrs):
        """Validate program requirements."""
        min_duration = attrs.get('min_duration')
        max_duration = attrs.get('max_duration')
        min_gpa = attrs.get('min_gpa')
        
        # Validate duration range
        if min_duration and max_duration and min_duration > max_duration:
            raise serializers.ValidationError("Minimum duration cannot be greater than maximum duration")
        
        # Validate GPA range
        if min_gpa and (min_gpa < 0 or min_gpa > 10):
            raise serializers.ValidationError("GPA must be between 0 and 10")
        
        # Validate eligible years
        eligible_years = attrs.get('eligible_years', [])
        if eligible_years:
            for year in eligible_years:
                if not isinstance(year, int) or year < 1 or year > 10:
                    raise serializers.ValidationError("Eligible years must be integers between 1 and 10")
        
        # Validate language requirements
        language_requirements = attrs.get('language_requirements', {})
        if language_requirements and not isinstance(language_requirements, dict):
            raise serializers.ValidationError("Language requirements must be a valid JSON object")
        
        return attrs


class ProgramRequirementsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing program requirements.
    """
    
    duration_range = serializers.SerializerMethodField()
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramRequirements
        fields = [
            'id', 'name', 'duration_range', 'min_gpa', 'programs_count'
        ]
    
    def get_duration_range(self, obj):
        """Get formatted duration range."""
        if obj.min_duration == obj.max_duration:
            return f"{obj.min_duration} {obj.get_duration_unit_display()}"
        return f"{obj.min_duration}-{obj.max_duration} {obj.get_duration_unit_display()}"
    
    def get_programs_count(self, obj):
        """Get count of exchange programs using these requirements."""
        if hasattr(obj, 'exchangeprogram_set'):
            return obj.exchangeprogram_set.count()
        return 0


class ProgramRequirementsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating program requirements.
    """
    
    class Meta:
        model = ProgramRequirements
        fields = [
            'name', 'min_duration', 'max_duration', 'duration_unit',
            'min_gpa', 'language_requirements', 'eligible_degrees',
            'eligible_years', 'student_semesters_remaining_after_exchange'
        ]
    
    def validate(self, attrs):
        """Validate new program requirements."""
        min_duration = attrs.get('min_duration')
        max_duration = attrs.get('max_duration')
        min_gpa = attrs.get('min_gpa')
        
        # Validate duration range
        if min_duration and max_duration and min_duration > max_duration:
            raise serializers.ValidationError("Minimum duration cannot be greater than maximum duration")
        
        # Validate GPA
        if min_gpa and (min_gpa < 0 or min_gpa > 10):
            raise serializers.ValidationError("GPA must be between 0 and 10")
        
        # Validate eligible years
        eligible_years = attrs.get('eligible_years', [])
        if eligible_years:
            if not isinstance(eligible_years, list):
                raise serializers.ValidationError("Eligible years must be a list")
            for year in eligible_years:
                if not isinstance(year, int) or year < 1 or year > 10:
                    raise serializers.ValidationError("Eligible years must be integers between 1 and 10")
        
        # Validate language requirements format
        language_requirements = attrs.get('language_requirements', {})
        if language_requirements:
            if not isinstance(language_requirements, dict):
                raise serializers.ValidationError("Language requirements must be a dictionary")
            
            # Validate each language requirement
            for language, requirement in language_requirements.items():
                if not isinstance(language, str) or not isinstance(requirement, str):
                    raise serializers.ValidationError("Language requirements must be string key-value pairs")
        
        # Validate eligible degrees
        eligible_degrees = attrs.get('eligible_degrees', [])
        if eligible_degrees and not isinstance(eligible_degrees, list):
            raise serializers.ValidationError("Eligible degrees must be a list")
        
        # Validate remaining semesters
        remaining_semesters = attrs.get('student_semesters_remaining_after_exchange', [])
        if remaining_semesters:
            if not isinstance(remaining_semesters, list):
                raise serializers.ValidationError("Student semesters remaining must be a list")
            for semester in remaining_semesters:
                if not isinstance(semester, int) or semester < 0:
                    raise serializers.ValidationError("Remaining semesters must be non-negative integers")
        
        return attrs


class ProgramRequirementsDetailSerializer(ProgramRequirementsSerializer):
    """
    Detailed serializer for program requirements with related programs.
    """
    
    related_programs = serializers.SerializerMethodField()
    eligibility_summary = serializers.SerializerMethodField()
    
    class Meta(ProgramRequirementsSerializer.Meta):
        fields = ProgramRequirementsSerializer.Meta.fields + ['related_programs', 'eligibility_summary']
    
    def get_related_programs(self, obj):
        """Get related exchange programs (avoid circular import)."""
        if hasattr(obj, 'exchangeprogram_set'):
            # Use a simple serializer to avoid circular imports
            programs = obj.exchangeprogram_set.all()[:5]  # Limit to 5 for performance
            return [{'id': p.id, 'name': p.name, 'code': p.code} for p in programs]
        return []
    
    def get_eligibility_summary(self, obj):
        """Get summary of eligibility requirements."""
        summary = {}
        
        if obj.min_gpa:
            summary['minimum_gpa'] = float(obj.min_gpa)
        
        if obj.eligible_years:
            summary['eligible_years'] = obj.eligible_years
        
        if obj.language_requirements:
            summary['language_requirements'] = obj.language_requirements
        
        if obj.eligible_degrees:
            summary['eligible_degrees'] = obj.eligible_degrees
        
        if obj.student_semesters_remaining_after_exchange:
            summary['min_remaining_semesters'] = min(obj.student_semesters_remaining_after_exchange)
        
        return summary


class ProgramRequirementsCheckSerializer(serializers.Serializer):
    """
    Serializer for checking student eligibility against program requirements.
    """
    
    student_profile = serializers.DictField(
        help_text="Student profile data for eligibility check"
    )
    requirements_id = serializers.IntegerField()
    
    def validate_requirements_id(self, value):
        """Validate requirements exist."""
        try:
            ProgramRequirements.objects.get(id=value)
        except ProgramRequirements.DoesNotExist:
            raise serializers.ValidationError("Invalid requirements ID")
        return value
    
    def validate_student_profile(self, value):
        """Validate student profile format."""
        required_fields = ['gpa', 'degree', 'year']
        missing_fields = [field for field in required_fields if field not in value]
        
        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields: {missing_fields}")
        
        # Validate GPA
        gpa = value.get('gpa')
        if gpa is not None:
            try:
                gpa_val = float(gpa)
                if gpa_val < 0 or gpa_val > 10:
                    raise serializers.ValidationError("GPA must be between 0 and 10")
            except (ValueError, TypeError):
                raise serializers.ValidationError("GPA must be a number")
        
        # Validate year
        year = value.get('year')
        if year is not None:
            try:
                year_val = int(year)
                if year_val < 1 or year_val > 10:
                    raise serializers.ValidationError("Year must be between 1 and 10")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Year must be an integer")
        
        return value
    
    def check_eligibility(self):
        """Check if student meets requirements."""
        requirements_id = self.validated_data['requirements_id']
        student_profile = self.validated_data['student_profile']
        
        try:
            requirements = ProgramRequirements.objects.get(id=requirements_id)
            
            # Use the exchange program eligibility check method if available
            if hasattr(requirements, 'is_student_eligible'):
                eligible, reason = requirements.is_student_eligible(student_profile)
                return {
                    'eligible': eligible,
                    'reason': reason,
                    'requirements': ProgramRequirementsSerializer(requirements).data
                }
            else:
                # Manual eligibility check
                return self._manual_eligibility_check(requirements, student_profile)
        
        except ProgramRequirements.DoesNotExist:
            raise serializers.ValidationError("Requirements not found")
    
    def _manual_eligibility_check(self, requirements, student_profile):
        """Manual eligibility check implementation."""
        eligible = True
        reasons = []
        
        # Check GPA
        if requirements.min_gpa and student_profile.get('gpa'):
            if float(student_profile['gpa']) < float(requirements.min_gpa):
                eligible = False
                reasons.append(f"GPA requirement not met (minimum: {requirements.min_gpa})")
        
        # Check degree
        if requirements.eligible_degrees and student_profile.get('degree'):
            if student_profile['degree'] not in requirements.eligible_degrees:
                eligible = False
                reasons.append("Degree program not eligible")
        
        # Check year
        if requirements.eligible_years and student_profile.get('year'):
            if int(student_profile['year']) not in requirements.eligible_years:
                eligible = False
                reasons.append("Academic year not eligible")
        
        # Check remaining semesters
        if requirements.student_semesters_remaining_after_exchange and student_profile.get('semesters_remaining'):
            min_required = min(requirements.student_semesters_remaining_after_exchange)
            if int(student_profile['semesters_remaining']) < min_required:
                eligible = False
                reasons.append(f"Insufficient remaining semesters (minimum: {min_required})")
        
        return {
            'eligible': eligible,
            'reason': '; '.join(reasons) if reasons else 'All requirements met',
            'requirements': ProgramRequirementsSerializer(requirements).data
        }
