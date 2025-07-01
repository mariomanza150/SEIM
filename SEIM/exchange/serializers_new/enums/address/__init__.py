"""
Address enum serializers for the exchange application.

Handles serialization for geographical reference data.
"""

from rest_framework import serializers
from ....models import Country, State, City
from ...base import BaseSerializer


class CountrySerializer(BaseSerializer):
    """
    Serializer for Country model.
    """
    
    class Meta:
        model = Country
        fields = '__all__'
    
    def validate_iso_code(self, value):
        """Validate ISO code format and uniqueness."""
        if not value or len(value) != 3:
            raise serializers.ValidationError("ISO code must be exactly 3 characters")
        
        value = value.upper()
        
        # Check uniqueness (excluding current instance if updating)
        qs = Country.objects.filter(iso_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("ISO code must be unique")
        
        return value
    
    def validate_name(self, value):
        """Validate country name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Country name cannot be empty")
        return value.strip()


class CountryListSerializer(BaseSerializer):
    """
    Simplified serializer for listing countries.
    """
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'region']


class StateSerializer(BaseSerializer):
    """
    Serializer for State model.
    """
    
    class Meta:
        model = State
        fields = '__all__'
    
    def validate_abbreviation(self, value):
        """Validate state abbreviation."""
        if not value or not value.strip():
            raise serializers.ValidationError("State abbreviation cannot be empty")
        
        value = value.upper().strip()
        
        # Check uniqueness (excluding current instance if updating)
        qs = State.objects.filter(abbreviation=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("State abbreviation must be unique")
        
        return value
    
    def validate_name(self, value):
        """Validate state name."""
        if not value or not value.strip():
            raise serializers.ValidationError("State name cannot be empty")
        return value.strip()


class StateListSerializer(BaseSerializer):
    """
    Simplified serializer for listing states.
    """
    
    class Meta:
        model = State
        fields = ['id', 'name', 'abbreviation']


class CitySerializer(BaseSerializer):
    """
    Serializer for City model.
    """
    
    country = CountryListSerializer(read_only=True)
    state = StateListSerializer(read_only=True)
    country_id = serializers.IntegerField(write_only=True, required=False)
    state_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = City
        fields = '__all__'
    
    def validate_country_id(self, value):
        """Validate country exists."""
        if value:
            try:
                Country.objects.get(id=value)
            except Country.DoesNotExist:
                raise serializers.ValidationError("Invalid country ID")
        return value
    
    def validate_state_id(self, value):
        """Validate state exists."""
        if value:
            try:
                State.objects.get(id=value)
            except State.DoesNotExist:
                raise serializers.ValidationError("Invalid state ID")
        return value


class CityListSerializer(BaseSerializer):
    """
    Simplified serializer for listing cities.
    """
    
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'country_name', 'state_name']


class CountryWithStatesSerializer(CountrySerializer):
    """
    Country serializer with related states.
    """
    
    states = StateListSerializer(many=True, read_only=True)
    
    class Meta(CountrySerializer.Meta):
        fields = CountrySerializer.Meta.fields + ['states']


class StateWithCitiesSerializer(StateSerializer):
    """
    State serializer with related cities.
    """
    
    cities = CityListSerializer(many=True, read_only=True)
    
    class Meta(StateSerializer.Meta):
        fields = StateSerializer.Meta.fields + ['cities']


class AddressBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk address data operations.
    """
    
    countries = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of countries to create"
    )
    states = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of states to create"
    )
    cities = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of cities to create"
    )
    
    def create(self, validated_data):
        """Create bulk address data."""
        results = {
            'countries': [],
            'states': [],
            'cities': []
        }
        
        # Create countries first
        if 'countries' in validated_data:
            for country_data in validated_data['countries']:
                country_serializer = CountrySerializer(data=country_data)
                if country_serializer.is_valid():
                    country = country_serializer.save()
                    results['countries'].append(country)
                else:
                    raise serializers.ValidationError({
                        'countries': country_serializer.errors
                    })
        
        # Create states
        if 'states' in validated_data:
            for state_data in validated_data['states']:
                state_serializer = StateSerializer(data=state_data)
                if state_serializer.is_valid():
                    state = state_serializer.save()
                    results['states'].append(state)
                else:
                    raise serializers.ValidationError({
                        'states': state_serializer.errors
                    })
        
        # Create cities
        if 'cities' in validated_data:
            for city_data in validated_data['cities']:
                city_serializer = CitySerializer(data=city_data)
                if city_serializer.is_valid():
                    city = city_serializer.save()
                    results['cities'].append(city)
                else:
                    raise serializers.ValidationError({
                        'cities': city_serializer.errors
                    })
        
        return results


class GeographicalHierarchySerializer(serializers.Serializer):
    """
    Serializer for geographical hierarchy data.
    """
    
    country_id = serializers.IntegerField(required=False)
    state_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        """Validate geographical hierarchy."""
        country_id = attrs.get('country_id')
        state_id = attrs.get('state_id')
        
        if state_id and not country_id:
            # If state is provided, we might want to auto-determine country
            # This depends on your data model relationships
            pass
        
        return attrs
    
    def to_representation(self, instance):
        """Return hierarchical geographical data."""
        country_id = instance.get('country_id')
        state_id = instance.get('state_id')
        
        result = {}
        
        if country_id:
            try:
                country = Country.objects.get(id=country_id)
                result['country'] = CountrySerializer(country).data
                
                # Get states for this country
                states = State.objects.filter(country=country) if hasattr(State, 'country') else State.objects.all()
                result['states'] = StateListSerializer(states, many=True).data
                
                if state_id:
                    try:
                        state = State.objects.get(id=state_id)
                        result['selected_state'] = StateSerializer(state).data
                        
                        # Get cities for this state
                        cities = City.objects.filter(state=state) if hasattr(City, 'state') else City.objects.all()
                        result['cities'] = CityListSerializer(cities, many=True).data
                    except State.DoesNotExist:
                        pass
            except Country.DoesNotExist:
                pass
        
        return result
