from rest_framework import serializers
from SEIM.exchange.models.academic.course import Course
from SEIM.exchange.models.academic.course_category import CourseCategory
from SEIM.exchange.models.academic.degree import Degree
from SEIM.exchange.models.academic.exchange_program import ExchangeProgram
from SEIM.exchange.models.academic.funding import Funding
from SEIM.exchange.models.academic.language import Language

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'

class ExchangeProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProgram
        fields = '__all__'

class FundingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funding
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'