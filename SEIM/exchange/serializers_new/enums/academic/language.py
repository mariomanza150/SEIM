"""
Language serializers for the exchange application.

Handles serialization for language definitions, proficiency levels, and tests.
"""

from rest_framework import serializers
from ....models import Language, ProficiencyLevels, LanguageProficiencyTest
from ...base import TimestampedModelSerializer


class ProficiencyLevelsSerializer(TimestampedModelSerializer):
    """
    Serializer for ProficiencyLevels model.
    """
    
    scale_type_display = serializers.CharField(source='get_scale_type_display', read_only=True)
    level_range = serializers.SerializerMethodField()
    
    class Meta:
        model = ProficiencyLevels
        fields = '__all__'
    
    def get_level_range(self, obj):
        """Get formatted level range."""
        range_str = f"{obj.min_level} - {obj.max_level}"
        if obj.has_plus:
            range_str += " (with + levels)"
        return range_str
    
    def validate(self, attrs):
        """Validate proficiency levels."""
        scale_type = attrs.get('scale_type')
        min_level = attrs.get('min_level')
        max_level = attrs.get('max_level')
        
        if scale_type == 'NUMERIC':
            # Validate numeric levels
            try:
                min_val = float(min_level) if min_level else 0
                max_val = float(max_level) if max_level else 0
                if min_val >= max_val:
                    raise serializers.ValidationError("Max level must be greater than min level")
            except ValueError:
                raise serializers.ValidationError("Numeric scale requires numeric min/max levels")
        
        elif scale_type == 'ALPHABETIC':
            # Validate alphabetic levels (A1, A2, B1, B2, C1, C2, etc.)
            valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            if min_level and min_level not in valid_levels:
                raise serializers.ValidationError(f"Invalid min level for alphabetic scale: {min_level}")
            if max_level and max_level not in valid_levels:
                raise serializers.ValidationError(f"Invalid max level for alphabetic scale: {max_level}")
        
        return attrs


class LanguageSerializer(TimestampedModelSerializer):
    """
    Serializer for Language model.
    """
    
    proficiency_tests = serializers.SerializerMethodField()
    
    class Meta:
        model = Language
        fields = '__all__'
    
    def get_proficiency_tests(self, obj):
        """Get available proficiency tests for this language."""
        if hasattr(obj, 'languageproficiencytest_set'):
            tests = obj.languageproficiencytest_set.all()
            return LanguageProficiencyTestListSerializer(tests, many=True).data
        return []
    
    def validate_iso_code(self, value):
        """Validate ISO language code."""
        if not value or len(value) < 2:
            raise serializers.ValidationError("ISO code must be at least 2 characters")
        
        value = value.lower()
        
        # Check uniqueness (excluding current instance if updating)
        qs = Language.objects.filter(iso_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("ISO code must be unique")
        
        return value


class LanguageListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing languages.
    """
    
    test_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Language
        fields = ['id', 'name', 'iso_code', 'test_count']
    
    def get_test_count(self, obj):
        """Get count of proficiency tests for this language."""
        if hasattr(obj, 'languageproficiencytest_set'):
            return obj.languageproficiencytest_set.count()
        return 0


class LanguageProficiencyTestSerializer(TimestampedModelSerializer):
    """
    Serializer for LanguageProficiencyTest model.
    """
    
    language = LanguageListSerializer(read_only=True)
    scale = ProficiencyLevelsSerializer(read_only=True)
    language_id = serializers.IntegerField(write_only=True, required=False)
    scale_id = serializers.IntegerField(write_only=True, required=False)
    score_range = serializers.SerializerMethodField()
    
    class Meta:
        model = LanguageProficiencyTest
        fields = '__all__'
    
    def get_score_range(self, obj):
        """Get formatted score range."""
        return f"{obj.min_score} - {obj.max_score}"
    
    def validate_language_id(self, value):
        """Validate language exists."""
        if value:
            try:
                Language.objects.get(id=value)
            except Language.DoesNotExist:
                raise serializers.ValidationError("Invalid language ID")
        return value
    
    def validate_scale_id(self, value):
        """Validate scale exists."""
        if value:
            try:
                ProficiencyLevels.objects.get(id=value)
            except ProficiencyLevels.DoesNotExist:
                raise serializers.ValidationError("Invalid scale ID")
        return value
    
    def validate(self, attrs):
        """Validate test scores based on scale type."""
        scale_id = attrs.get('scale_id')
        min_score = attrs.get('min_score')
        max_score = attrs.get('max_score')
        
        if scale_id and min_score and max_score:
            try:
                scale = ProficiencyLevels.objects.get(id=scale_id)
                
                if scale.scale_type == 'NUMERIC':
                    # Validate numeric scores
                    try:
                        min_val = float(min_score)
                        max_val = float(max_score)
                        scale_min = float(scale.min_level)
                        scale_max = float(scale.max_level)
                        
                        if min_val < scale_min or max_val > scale_max:
                            raise serializers.ValidationError(
                                f"Scores must be within scale range: {scale.min_level} - {scale.max_level}"
                            )
                        
                        if min_val >= max_val:
                            raise serializers.ValidationError("Max score must be greater than min score")
                    except ValueError:
                        raise serializers.ValidationError("Numeric scale requires numeric scores")
                
            except ProficiencyLevels.DoesNotExist:
                pass  # Will be caught by scale_id validation
        
        return attrs


class LanguageProficiencyTestListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing language proficiency tests.
    """
    
    language_name = serializers.CharField(source='language.name', read_only=True)
    scale_name = serializers.CharField(source='scale.name', read_only=True)
    score_range = serializers.SerializerMethodField()
    
    class Meta:
        model = LanguageProficiencyTest
        fields = ['id', 'name', 'language_name', 'scale_name', 'score_range']
    
    def get_score_range(self, obj):
        """Get formatted score range."""
        return f"{obj.min_score} - {obj.max_score}"


class LanguageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating languages.
    """
    
    class Meta:
        model = Language
        fields = ['name', 'iso_code']
    
    def validate_iso_code(self, value):
        """Validate ISO code is unique."""
        if not value or len(value) < 2:
            raise serializers.ValidationError("ISO code must be at least 2 characters")
        
        value = value.lower()
        
        if Language.objects.filter(iso_code=value).exists():
            raise serializers.ValidationError("ISO code must be unique")
        
        return value


class LanguageBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk language operations.
    """
    
    languages = serializers.ListField(
        child=LanguageCreateSerializer(),
        min_length=1,
        help_text="List of languages to create"
    )
    
    def create(self, validated_data):
        """Create multiple languages."""
        languages_data = validated_data['languages']
        
        # Check for duplicate ISO codes in the batch
        iso_codes = [lang['iso_code'].lower() for lang in languages_data]
        if len(iso_codes) != len(set(iso_codes)):
            raise serializers.ValidationError("Duplicate ISO codes in batch")
        
        # Check for existing ISO codes
        existing_codes = Language.objects.filter(
            iso_code__in=iso_codes
        ).values_list('iso_code', flat=True)
        
        if existing_codes:
            raise serializers.ValidationError(
                f"ISO codes already exist: {list(existing_codes)}"
            )
        
        # Create languages
        languages = []
        for lang_data in languages_data:
            lang = Language(**lang_data)
            languages.append(lang)
        
        return Language.objects.bulk_create(languages)


class LanguageRequirementSerializer(serializers.Serializer):
    """
    Serializer for language requirements in exchange programs.
    """
    
    language_id = serializers.IntegerField()
    required_level = serializers.CharField()
    test_id = serializers.IntegerField(required=False)
    min_score = serializers.CharField(required=False)
    
    def validate_language_id(self, value):
        """Validate language exists."""
        try:
            Language.objects.get(id=value)
        except Language.DoesNotExist:
            raise serializers.ValidationError("Invalid language ID")
        return value
    
    def validate_test_id(self, value):
        """Validate test exists."""
        if value:
            try:
                LanguageProficiencyTest.objects.get(id=value)
            except LanguageProficiencyTest.DoesNotExist:
                raise serializers.ValidationError("Invalid test ID")
        return value
    
    def validate(self, attrs):
        """Validate language requirement."""
        test_id = attrs.get('test_id')
        min_score = attrs.get('min_score')
        language_id = attrs.get('language_id')
        
        # If test is specified, validate the score is within test range
        if test_id and min_score:
            try:
                test = LanguageProficiencyTest.objects.get(id=test_id)
                
                # Verify test is for the specified language
                if test.language_id != language_id:
                    raise serializers.ValidationError("Test does not match the specified language")
                
                # Validate score is within test range
                if test.scale.scale_type == 'NUMERIC':
                    try:
                        score_val = float(min_score)
                        test_min = float(test.min_score)
                        test_max = float(test.max_score)
                        
                        if score_val < test_min or score_val > test_max:
                            raise serializers.ValidationError(
                                f"Score must be within test range: {test.min_score} - {test.max_score}"
                            )
                    except ValueError:
                        raise serializers.ValidationError("Numeric test requires numeric score")
                
            except LanguageProficiencyTest.DoesNotExist:
                pass  # Will be caught by test_id validation
        
        return attrs


class LanguageCompetencySerializer(serializers.Serializer):
    """
    Serializer for student language competency.
    """
    
    language_id = serializers.IntegerField()
    proficiency_level = serializers.CharField()
    test_id = serializers.IntegerField(required=False)
    test_score = serializers.CharField(required=False)
    certificate_file = serializers.FileField(required=False)
    verified = serializers.BooleanField(default=False, read_only=True)
    
    def validate_language_id(self, value):
        """Validate language exists."""
        try:
            Language.objects.get(id=value)
        except Language.DoesNotExist:
            raise serializers.ValidationError("Invalid language ID")
        return value
    
    def validate_test_id(self, value):
        """Validate test exists and matches language."""
        if value:
            try:
                test = LanguageProficiencyTest.objects.get(id=value)
                language_id = self.initial_data.get('language_id')
                if language_id and test.language_id != language_id:
                    raise serializers.ValidationError("Test does not match the specified language")
            except LanguageProficiencyTest.DoesNotExist:
                raise serializers.ValidationError("Invalid test ID")
        return value
