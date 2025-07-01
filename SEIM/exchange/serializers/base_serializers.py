from rest_framework import serializers
from SEIM.exchange.models.base_models.base import Institution, Student, StudentProfile, StudentDashboard

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class StudentDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDashboard
        fields = '__all__'
