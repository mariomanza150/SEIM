from rest_framework import serializers
from SEIM.exchange.models.applications.timeline import Timeline

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
