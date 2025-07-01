from rest_framework import serializers
from SEIM.exchange.models.places.campus import Campus
from SEIM.exchange.models.places.address.city import City
from SEIM.exchange.models.places.address.country import Country
from SEIM.exchange.models.places.questionnaire.question import Question
from SEIM.exchange.models.places.address.state import State
from SEIM.exchange.models.places.university import University

class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'
