from rest_framework import serializers
from SEIM.exchange.models.applications.application_answer import ApplicationAnswer
from SEIM.exchange.models.applications.application_status import ApplicationStatus
from SEIM.exchange.models.applications.comment import Comment
from SEIM.exchange.models.applications.document import Document
from SEIM.exchange.models.applications.document_type import DocumentType
from SEIM.exchange.models.applications.exchange import Exchange
from SEIM.exchange.models.applications.timeline import Timeline

class ApplicationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAnswer
        fields = '__all__'

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'

class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exchange
        fields = '__all__'

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'
