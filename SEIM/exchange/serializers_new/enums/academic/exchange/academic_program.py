"""
Exchange Program serializers for the exchange application.

Handles serialization for the main ExchangeProgram model with comprehensive functionality.
"""

from rest_framework import serializers
from .....models import ExchangeProgram
from ....base import TimestampedModelSerializer
from .funding import FundingTypeListSerializer
from .program_requirements import ProgramRequirementsSerializer


class ExchangeProgramListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing exchange programs.
    """
    
    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)
    is_application_open = serializers.BooleanField(read_only=True)
    available_slots = serializers.SerializerMethodField()
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    countries_count = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExchangeProgram
        fields = [
            'id', 'name', 'code', 'program_type', 'program_type_display',
            'description', 'countries_count', 'is_active', 'is_application_open',
            'available_slots', 'duration_display', 'website_url', 'applications_count'
        ]
    
    def get_available_slots(self, obj):
        """Get available slots for the program."""
        return obj.get_available_slots()
    
    def get_countries_count(self, obj):
        """Get count of countries covered."""
        return len(obj.countries) if obj.countries else 0
    
    def get_applications_count(self, obj):
        """Get count of applications for this program."""
        if hasattr(obj, 'exchange_set'):
            return obj.exchange_set.count()
        return 0


class ExchangeProgramDetailSerializer(TimestampedModelSerializer):
    """
    Detailed serializer for exchange programs with all information.
    """
    
    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)
    is_application_open = serializers.BooleanField(read_only=True)
    available_slots = serializers.SerializerMethodField()
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    coordinator = serializers.StringRelatedField(read_only=True)
    funding_types = FundingTypeListSerializer(many=True, read_only=True)
    program_requirements = ProgramRequirementsSerializer(read_only=True)
    required_documents_display = serializers.CharField(source='get_required_documents_display', read_only=True)
    partner_universities_by_country = serializers.SerializerMethodField()
    has_funding = serializers.BooleanField(read_only=True)
    applications_statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = ExchangeProgram
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_available_slots(self, obj):
        """Get available slots for the program."""
        return obj.get_available_slots()
    
    def get_partner_universities_by_country(self, obj):
        """Get partner universities grouped by country."""
        return obj.get_partner_universities_by_country()
    
    def get_applications_statistics(self, obj):
        """Get application statistics for this program."""
        if hasattr(obj, 'exchange_set'):
            exchanges = obj.exchange_set.all()
            total = exchanges.count()
            
            if total == 0:
                return {'total': 0}
            
            # Count by status
            status_counts = {}
            for exchange in exchanges:
                status = exchange.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total': total,
                'by_status': status_counts,
                'approval_rate': round((status_counts.get('APPROVED', 0) / total) * 100, 2) if total > 0 else 0
            }
        return {'total': 0}


class ExchangeProgramSerializer(TimestampedModelSerializer):
    """
    Standard serializer for ExchangeProgram model.
    """
    
    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)
    is_application_open = serializers.BooleanField(read_only=True)
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    coordinator = serializers.StringRelatedField(read_only=True)
    has_funding = serializers.BooleanField(read_only=True)
    
    # Write-only fields for relationships
    coordinator_id = serializers.IntegerField(write_only=True, required=False)
    program_requirements_id = serializers.IntegerField(write_only=True, required=False)
    funding_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of funding type IDs"
    )
    
    class Meta:
        model = ExchangeProgram
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_coordinator_id(self, value):
        """Validate coordinator exists."""
        if value:
            from django.contrib.auth.models import User
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid coordinator ID")
        return value
    
    def validate_program_requirements_id(self, value):
        """Validate program requirements exist."""
        if value:
            from .....models import ProgramRequirements
            try:
                ProgramRequirements.objects.get(id=value)
            except ProgramRequirements.DoesNotExist:
                raise serializers.ValidationError("Invalid program requirements ID")
        return value
    
    def validate_funding_type_ids(self, value):
        """Validate funding types exist."""
        if value:
            from .....models import FundingType
            existing_ids = set(FundingType.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Invalid funding type IDs: {list(invalid_ids)}")
        return value
    
    def validate_code(self, value):
        """Validate program code is unique."""
        if value:
            qs = ExchangeProgram.objects.filter(code=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError("Program code must be unique")
        
        return value
    
    def validate(self, attrs):
        """Validate exchange program data."""
        # Validate application dates
        app_start = attrs.get('application_start_date')
        app_end = attrs.get('application_end_date')
        
        if app_start and app_end and app_start >= app_end:
            raise serializers.ValidationError("Application start date must be before end date")
        
        # Validate funding amount and currency
        funding_amount = attrs.get('funding_amount')
        funding_currency = attrs.get('funding_currency')
        
        if funding_amount and funding_amount < 0:
            raise serializers.ValidationError("Funding amount cannot be negative")
        
        if funding_amount and not funding_currency:
            raise serializers.ValidationError("Funding currency is required when amount is specified")
        
        # Validate max participants
        max_participants = attrs.get('max_participants')
        if max_participants and max_participants <= 0:
            raise serializers.ValidationError("Max participants must be greater than zero")
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update exchange program with relationship handling."""
        # Handle funding types separately
        funding_type_ids = validated_data.pop('funding_type_ids', None)
        
        # Update main fields
        instance = super().update(instance, validated_data)
        
        # Update funding types if provided
        if funding_type_ids is not None:
            from .....models import FundingType
            funding_types = FundingType.objects.filter(id__in=funding_type_ids)
            instance.funding_types.set(funding_types)
        
        return instance


class ExchangeProgramCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating exchange programs.
    """
    
    coordinator_id = serializers.IntegerField(required=False)
    program_requirements_id = serializers.IntegerField(required=False)
    funding_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of funding type IDs"
    )
    
    class Meta:
        model = ExchangeProgram
        fields = [
            'name', 'code', 'program_type', 'description', 'partner_universities',
            'countries', 'application_start_date', 'application_end_date',
            'coordinator_id', 'program_requirements_id', 'funding_type_ids',
            'funding_amount', 'funding_currency', 'max_participants', 'is_active',
            'priority_order', 'required_documents', 'website_url', 'contact_email',
            'additional_info'
        ]
    
    def validate_coordinator_id(self, value):
        """Validate coordinator exists."""
        if value:
            from django.contrib.auth.models import User
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid coordinator ID")
        return value
    
    def validate_program_requirements_id(self, value):
        """Validate program requirements exist."""
        if value:
            from .....models import ProgramRequirements
            try:
                ProgramRequirements.objects.get(id=value)
            except ProgramRequirements.DoesNotExist:
                raise serializers.ValidationError("Invalid program requirements ID")
        return value
    
    def validate_funding_type_ids(self, value):
        """Validate funding types exist."""
        if value:
            from .....models import FundingType
            existing_ids = set(FundingType.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Invalid funding type IDs: {list(invalid_ids)}")
        return value
    
    def validate_code(self, value):
        """Validate program code is unique."""
        if value and ExchangeProgram.objects.filter(code=value).exists():
            raise serializers.ValidationError("Program code must be unique")
        return value
    
    def create(self, validated_data):
        """Create exchange program with relationships."""
        funding_type_ids = validated_data.pop('funding_type_ids', [])
        
        # Create the program
        program = super().create(validated_data)
        
        # Set funding types
        if funding_type_ids:
            from .....models import FundingType
            funding_types = FundingType.objects.filter(id__in=funding_type_ids)
            program.funding_types.set(funding_types)
        
        return program


class ExchangeProgramEligibilitySerializer(serializers.Serializer):
    """
    Serializer for checking student eligibility for exchange programs.
    """
    
    student_profile = serializers.DictField(
        help_text="Student profile data for eligibility check"
    )
    program_id = serializers.IntegerField(required=False)
    
    def validate_program_id(self, value):
        """Validate program exists."""
        if value:
            try:
                ExchangeProgram.objects.get(id=value)
            except ExchangeProgram.DoesNotExist:
                raise serializers.ValidationError("Invalid program ID")
        return value
    
    def validate_student_profile(self, value):
        """Validate student profile format."""
        required_fields = ['gpa', 'degree', 'year']
        missing_fields = [field for field in required_fields if field not in value]
        
        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields: {missing_fields}")
        
        return value
    
    def check_eligibility(self):
        """Check eligibility for programs."""
        student_profile = self.validated_data['student_profile']
        program_id = self.validated_data.get('program_id')
        
        if program_id:
            # Check specific program
            program = ExchangeProgram.objects.get(id=program_id)
            eligible, reason = program.is_student_eligible(student_profile)
            
            return {
                'program': ExchangeProgramListSerializer(program).data,
                'eligible': eligible,
                'reason': reason
            }
        else:
            # Check all active programs
            programs = ExchangeProgram.objects.filter(is_active=True)
            results = []
            
            for program in programs:
                eligible, reason = program.is_student_eligible(student_profile)
                results.append({
                    'program': ExchangeProgramListSerializer(program).data,
                    'eligible': eligible,
                    'reason': reason
                })
            
            # Sort by eligibility (eligible first)
            results.sort(key=lambda x: not x['eligible'])
            
            return {
                'total_programs': len(results),
                'eligible_count': len([r for r in results if r['eligible']]),
                'results': results
            }


class ExchangeProgramSearchSerializer(serializers.Serializer):
    """
    Serializer for searching exchange programs.
    """
    
    query = serializers.CharField(required=False, help_text="Search query")
    program_type = serializers.ChoiceField(
        choices=ExchangeProgram.PROGRAM_TYPES,
        required=False
    )
    countries = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Filter by countries"
    )
    is_active = serializers.BooleanField(required=False)
    has_funding = serializers.BooleanField(required=False)
    application_open = serializers.BooleanField(required=False)
    
    def filter_queryset(self, queryset):
        """Filter queryset based on search criteria."""
        query = self.validated_data.get('query')
        program_type = self.validated_data.get('program_type')
        countries = self.validated_data.get('countries')
        is_active = self.validated_data.get('is_active')
        has_funding = self.validated_data.get('has_funding')
        application_open = self.validated_data.get('application_open')
        
        if query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(code__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if program_type:
            queryset = queryset.filter(program_type=program_type)
        
        if countries:
            # Filter programs that include any of the specified countries
            from django.db.models import Q
            country_filters = Q()
            for country in countries:
                country_filters |= Q(countries__icontains=country)
            queryset = queryset.filter(country_filters)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        if has_funding is not None:
            if has_funding:
                queryset = queryset.filter(
                    Q(funding_types__isnull=False) | 
                    Q(funding_amount__gt=0)
                ).distinct()
            else:
                queryset = queryset.filter(
                    funding_types__isnull=True,
                    funding_amount__isnull=True
                )
        
        if application_open is not None:
            if application_open:
                from django.utils import timezone
                today = timezone.now().date()
                queryset = queryset.filter(
                    is_active=True,
                    application_start_date__lte=today,
                    application_end_date__gte=today
                )
            else:
                from django.utils import timezone
                today = timezone.now().date()
                queryset = queryset.exclude(
                    is_active=True,
                    application_start_date__lte=today,
                    application_end_date__gte=today
                )
        
        return queryset


class ExchangeProgramStatisticsSerializer(serializers.Serializer):
    """
    Serializer for exchange program statistics.
    """
    
    program_id = serializers.IntegerField(required=False)
    
    def validate_program_id(self, value):
        """Validate program exists."""
        if value:
            try:
                ExchangeProgram.objects.get(id=value)
            except ExchangeProgram.DoesNotExist:
                raise serializers.ValidationError("Invalid program ID")
        return value
    
    def get_statistics(self):
        """Get program statistics."""
        program_id = self.validated_data.get('program_id')
        
        if program_id:
            # Statistics for specific program
            program = ExchangeProgram.objects.get(id=program_id)
            return self._get_program_statistics(program)
        else:
            # Overall statistics
            return self._get_overall_statistics()
    
    def _get_program_statistics(self, program):
        """Get statistics for a specific program."""
        if not hasattr(program, 'exchange_set'):
            return {'program': ExchangeProgramListSerializer(program).data, 'statistics': {}}
        
        exchanges = program.exchange_set.all()
        total = exchanges.count()
        
        # Status distribution
        status_counts = {}
        for exchange in exchanges:
            status = exchange.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Monthly applications (last 12 months)
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        monthly_apps = exchanges.filter(
            created_at__date__gte=start_date
        ).extra(
            select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"}
        ).values('month').annotate(count=Count('id')).order_by('month')
        
        return {
            'program': ExchangeProgramListSerializer(program).data,
            'statistics': {
                'total_applications': total,
                'status_distribution': status_counts,
                'approval_rate': round((status_counts.get('APPROVED', 0) / total) * 100, 2) if total > 0 else 0,
                'available_slots': program.get_available_slots(),
                'monthly_applications': list(monthly_apps)
            }
        }
    
    def _get_overall_statistics(self):
        """Get overall program statistics."""
        programs = ExchangeProgram.objects.all()
        
        return {
            'total_programs': programs.count(),
            'active_programs': programs.filter(is_active=True).count(),
            'programs_by_type': dict(programs.values_list('program_type').annotate(Count('id'))),
            'programs_with_funding': programs.filter(
                Q(funding_types__isnull=False) | Q(funding_amount__gt=0)
            ).distinct().count(),
            'application_open_programs': len([p for p in programs if p.is_application_open()])
        }
