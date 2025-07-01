"""
Application Answer serializers for the exchange application.

Handles serialization for application answers to dynamic questions.
"""

from rest_framework import serializers
from ...models import ApplicationAnswer
from ..base import BaseSerializer


class ApplicationAnswerSerializer(BaseSerializer):
    """
    Serializer for ApplicationAnswer model.
    """
    
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    question_required = serializers.BooleanField(source='question.is_required', read_only=True)
    question_options = serializers.SerializerMethodField()
    display_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationAnswer
        fields = '__all__'
        read_only_fields = ['exchange', 'question']
    
    def get_question_options(self, obj):
        """Get question options if it's a select type question."""
        if hasattr(obj.question, 'options') and obj.question.question_type == 'select':
            return obj.question.options
        return None
    
    def get_display_answer(self, obj):
        """Get formatted display answer based on question type."""
        if obj.question.question_type == 'select' and obj.selected_option_id:
            # Find the option text from question options
            options = self.get_question_options(obj)
            if options:
                for option in options:
                    if option.get('id') == obj.selected_option_id:
                        return option.get('text', str(obj.selected_option_id))
            return str(obj.selected_option_id)
        elif obj.question.question_type == 'yes_no' and obj.answer_text:
            return 'Yes' if obj.answer_text.lower() in ['yes', 'true', '1'] else 'No'
        else:
            return obj.answer_text
    
    def validate(self, attrs):
        """Validate answer based on question type."""
        question = self.context.get('question')
        if not question:
            raise serializers.ValidationError("Question context is required")
        
        answer_text = attrs.get('answer_text')
        selected_option_id = attrs.get('selected_option_id')
        
        # Validate that appropriate field is provided based on question type
        if question.question_type == 'select':
            if not selected_option_id:
                raise serializers.ValidationError("selected_option_id is required for select questions")
            if answer_text:
                raise serializers.ValidationError("answer_text should not be provided for select questions")
        else:
            if not answer_text:
                if question.is_required:
                    raise serializers.ValidationError("answer_text is required for this question")
            if selected_option_id:
                raise serializers.ValidationError("selected_option_id should not be provided for non-select questions")
        
        # Validate yes/no questions
        if question.question_type == 'yes_no' and answer_text:
            valid_yes_no = ['yes', 'no', 'true', 'false', '1', '0']
            if answer_text.lower() not in valid_yes_no:
                raise serializers.ValidationError("Answer must be yes/no for yes_no questions")
        
        # Validate select option exists
        if question.question_type == 'select' and selected_option_id:
            if hasattr(question, 'options') and question.options:
                valid_option_ids = [opt.get('id') for opt in question.options if opt.get('id')]
                if selected_option_id not in valid_option_ids:
                    raise serializers.ValidationError("Invalid option selected")
        
        return attrs


class ApplicationAnswerListSerializer(BaseSerializer):
    """
    Simplified serializer for listing application answers.
    """
    
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    display_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationAnswer
        fields = [
            'id', 'question_text', 'question_type', 'display_answer'
        ]
    
    def get_display_answer(self, obj):
        """Get formatted display answer."""
        # Reuse logic from main serializer
        main_serializer = ApplicationAnswerSerializer()
        return main_serializer.get_display_answer(obj)


class ApplicationAnswerCreateSerializer(BaseSerializer):
    """
    Serializer for creating application answers.
    """
    
    question_id = serializers.IntegerField()
    
    class Meta:
        model = ApplicationAnswer
        fields = ['question_id', 'answer_text', 'selected_option_id']
    
    def create(self, validated_data):
        """Create answer with exchange and question from context."""
        question_id = validated_data.pop('question_id')
        
        # Get question and validate
        from ...models import Question
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question ID")
        
        validated_data['exchange'] = self.context['exchange']
        validated_data['question'] = question
        
        # Add question to context for validation
        self.context['question'] = question
        
        return super().create(validated_data)


class ApplicationAnswerUpdateSerializer(BaseSerializer):
    """
    Serializer for updating application answers.
    """
    
    class Meta:
        model = ApplicationAnswer
        fields = ['answer_text', 'selected_option_id']
    
    def validate(self, attrs):
        """Validate update with existing question."""
        # Add existing question to context for validation
        self.context['question'] = self.instance.question
        return super().validate(attrs)


class ApplicationAnswerBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on application answers.
    """
    
    answers = serializers.ListField(
        child=ApplicationAnswerCreateSerializer(),
        min_length=1,
        help_text="List of answers to create or update"
    )
    
    def create(self, validated_data):
        """Create or update multiple answers."""
        answers_data = validated_data['answers']
        exchange = self.context['exchange']
        
        created_answers = []
        updated_answers = []
        
        for answer_data in answers_data:
            question_id = answer_data['question_id']
            
            # Check if answer already exists
            existing_answer = ApplicationAnswer.objects.filter(
                exchange=exchange,
                question_id=question_id
            ).first()
            
            if existing_answer:
                # Update existing answer
                for field, value in answer_data.items():
                    if field != 'question_id':
                        setattr(existing_answer, field, value)
                existing_answer.save()
                updated_answers.append(existing_answer)
            else:
                # Create new answer
                answer_data['exchange'] = exchange
                answer = ApplicationAnswer.objects.create(**answer_data)
                created_answers.append(answer)
        
        return {
            'created': created_answers,
            'updated': updated_answers
        }


class ApplicationAnswerValidationSerializer(serializers.Serializer):
    """
    Serializer for validating answers completeness.
    """
    
    exchange_id = serializers.IntegerField()
    
    def validate_exchange_id(self, value):
        """Validate exchange exists and user has access."""
        from ...models import Exchange
        try:
            exchange = Exchange.objects.get(id=value)
        except Exchange.DoesNotExist:
            raise serializers.ValidationError("Invalid exchange ID")
        
        # Add access validation here if needed
        request = self.context.get('request')
        if request and request.user != exchange.student and not request.user.is_staff:
            raise serializers.ValidationError("Access denied to this exchange")
        
        return value
    
    def validate(self, attrs):
        """Check if all required questions are answered."""
        from ...models import Exchange, Question
        
        exchange_id = attrs['exchange_id']
        exchange = Exchange.objects.get(id=exchange_id)
        
        # Get all required questions for the current stage
        current_stage = self.get_current_stage(exchange)
        required_questions = Question.objects.filter(
            is_required=True,
            stage=current_stage
        )
        
        # Check which questions are missing answers
        answered_question_ids = set(
            exchange.application_answers.values_list('question_id', flat=True)
        )
        required_question_ids = set(required_questions.values_list('id', flat=True))
        missing_question_ids = required_question_ids - answered_question_ids
        
        if missing_question_ids:
            missing_questions = Question.objects.filter(id__in=missing_question_ids)
            missing_texts = [q.text for q in missing_questions]
            raise serializers.ValidationError({
                'missing_answers': f"Missing answers for required questions: {', '.join(missing_texts)}"
            })
        
        return attrs
    
    def get_current_stage(self, exchange):
        """Determine current stage based on exchange status."""
        # Map exchange status to document stages
        status_to_stage = {
            'DRAFT': 'APPLICATION',
            'SUBMITTED': 'APPLICATION', 
            'UNDER_REVIEW': 'REVIEW',
            'APPROVED': 'ACCEPTANCE',
            'COMPLETED': 'FINALIZATION'
        }
        return status_to_stage.get(exchange.status, 'APPLICATION')
