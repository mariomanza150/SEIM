"""
Degree serializers for the exchange application.

Handles serialization for degree program definitions and management.
"""

from rest_framework import serializers
from ....models import DegreeProgram
from ...base import TimestampedModelSerializer


class DegreeProgramSerializer(TimestampedModelSerializer):
    """
    Serializer for DegreeProgram model.
    """
    
    university = serializers.StringRelatedField(read_only=True)
    institution = serializers.StringRelatedField(read_only=True)
    campus = serializers.StringRelatedField(read_only=True)
    university_id = serializers.IntegerField(write_only=True, required=False)
    institution_id = serializers.IntegerField(write_only=True, required=False)
    campus_id = serializers.IntegerField(write_only=True, required=False)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DegreeProgram
        fields = '__all__'
    
    def get_full_name(self, obj):
        """Get full degree program name with institution."""
        if obj.university:
            return f"{obj.name} ({obj.university.name})"
        return obj.name
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def validate_institution_id(self, value):
        """Validate institution exists."""
        if value:
            from ....models import Institution
            try:
                Institution.objects.get(id=value)
            except Institution.DoesNotExist:
                raise serializers.ValidationError("Invalid institution ID")
        return value
    
    def validate_campus_id(self, value):
        """Validate campus exists."""
        if value:
            from ....models import Campus
            try:
                Campus.objects.get(id=value)
            except Campus.DoesNotExist:
                raise serializers.ValidationError("Invalid campus ID")
        return value
    
    def validate_code(self, value):
        """Validate degree code is unique within university."""
        if value:
            university_id = self.initial_data.get('university_id')
            if university_id:
                qs = DegreeProgram.objects.filter(code=value, university_id=university_id)
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                
                if qs.exists():
                    raise serializers.ValidationError("Degree code must be unique within university")
        
        return value


class DegreeProgramListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing degree programs.
    """
    
    university_name = serializers.CharField(source='university.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DegreeProgram
        fields = [
            'id', 'name', 'code', 'university_name', 'institution_name', 
            'campus_name', 'full_name'
        ]
    
    def get_full_name(self, obj):
        """Get full degree program name."""
        if obj.university:
            return f"{obj.name} ({obj.university.name})"
        return obj.name


class DegreeProgramCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating degree programs.
    """
    
    university_id = serializers.IntegerField()
    institution_id = serializers.IntegerField()
    campus_id = serializers.IntegerField()
    
    class Meta:
        model = DegreeProgram
        fields = ['name', 'code', 'university_id', 'institution_id', 'campus_id']
    
    def validate_university_id(self, value):
        """Validate university exists."""
        from ....models import University
        try:
            University.objects.get(id=value)
        except University.DoesNotExist:
            raise serializers.ValidationError("Invalid university ID")
        return value
    
    def validate_institution_id(self, value):
        """Validate institution exists."""
        from ....models import Institution
        try:
            Institution.objects.get(id=value)
        except Institution.DoesNotExist:
            raise serializers.ValidationError("Invalid institution ID")
        return value
    
    def validate_campus_id(self, value):
        """Validate campus exists."""
        from ....models import Campus
        try:
            Campus.objects.get(id=value)
        except Campus.DoesNotExist:
            raise serializers.ValidationError("Invalid campus ID")
        return value
    
    def validate(self, attrs):
        """Validate degree program data."""
        # Check if degree code is unique within university
        code = attrs.get('code')
        university_id = attrs.get('university_id')
        
        if code and university_id:
            if DegreeProgram.objects.filter(code=code, university_id=university_id).exists():
                raise serializers.ValidationError("Degree code must be unique within university")
        
        return attrs


class DegreeProgramBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk degree program operations.
    """
    
    degree_programs = serializers.ListField(
        child=DegreeProgramCreateSerializer(),
        min_length=1,
        help_text="List of degree programs to create"
    )
    
    def create(self, validated_data):
        """Create multiple degree programs."""
        programs_data = validated_data['degree_programs']
        
        # Check for duplicate codes within universities in the batch
        code_university_pairs = []
        for program_data in programs_data:
            code = program_data.get('code')
            university_id = program_data.get('university_id')
            if code and university_id:
                pair = (code, university_id)
                if pair in code_university_pairs:
                    raise serializers.ValidationError(
                        f"Duplicate code '{code}' for university ID {university_id} in batch"
                    )
                code_university_pairs.append(pair)
        
        # Check for existing codes
        for code, university_id in code_university_pairs:
            if DegreeProgram.objects.filter(code=code, university_id=university_id).exists():
                raise serializers.ValidationError(
                    f"Degree code '{code}' already exists for university ID {university_id}"
                )
        
        # Create degree programs
        degree_programs = []
        for program_data in programs_data:
            program = DegreeProgram(**program_data)
            degree_programs.append(program)
        
        return DegreeProgram.objects.bulk_create(degree_programs)


class DegreeProgramByUniversitySerializer(serializers.Serializer):
    """
    Serializer for grouping degree programs by university.
    """
    
    university_id = serializers.IntegerField(required=False)
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def to_representation(self, instance):
        """Return degree programs grouped by university."""
        university_id = instance.get('university_id')
        
        if university_id:
            # Get programs for specific university
            programs = DegreeProgram.objects.filter(university_id=university_id)
            return {
                'university_id': university_id,
                'degree_programs': DegreeProgramListSerializer(programs, many=True).data
            }
        else:
            # Group all programs by university
            from ....models import University
            universities = University.objects.all()
            result = []
            
            for university in universities:
                programs = DegreeProgram.objects.filter(university=university)
                if programs.exists():
                    result.append({
                        'university': {
                            'id': university.id,
                            'name': university.name
                        },
                        'degree_programs': DegreeProgramListSerializer(programs, many=True).data,
                        'total_count': programs.count()
                    })
            
            return result


class DegreeProgramSearchSerializer(serializers.Serializer):
    """
    Serializer for searching degree programs.
    """
    
    query = serializers.CharField(required=False, help_text="Search query for name or code")
    university_id = serializers.IntegerField(required=False)
    institution_id = serializers.IntegerField(required=False)
    campus_id = serializers.IntegerField(required=False)
    
    def validate_university_id(self, value):
        """Validate university exists."""
        if value:
            from ....models import University
            try:
                University.objects.get(id=value)
            except University.DoesNotExist:
                raise serializers.ValidationError("Invalid university ID")
        return value
    
    def validate_institution_id(self, value):
        """Validate institution exists."""
        if value:
            from ....models import Institution
            try:
                Institution.objects.get(id=value)
            except Institution.DoesNotExist:
                raise serializers.ValidationError("Invalid institution ID")
        return value
    
    def validate_campus_id(self, value):
        """Validate campus exists."""
        if value:
            from ....models import Campus
            try:
                Campus.objects.get(id=value)
            except Campus.DoesNotExist:
                raise serializers.ValidationError("Invalid campus ID")
        return value
    
    def filter_queryset(self, queryset):
        """Filter queryset based on search criteria."""
        query = self.validated_data.get('query')
        university_id = self.validated_data.get('university_id')
        institution_id = self.validated_data.get('institution_id')
        campus_id = self.validated_data.get('campus_id')
        
        if query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(code__icontains=query)
            )
        
        if university_id:
            queryset = queryset.filter(university_id=university_id)
        
        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)
        
        if campus_id:
            queryset = queryset.filter(campus_id=campus_id)
        
        return queryset
