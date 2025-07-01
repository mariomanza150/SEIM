"""
Comment and Review serializers for the exchange application.

Handles serialization for comments, reviews, and communication workflows.
"""

from rest_framework import serializers
from ...models import Comment, Review
from ..base import TimestampedModelSerializer, UserSerializer


class CommentSerializer(TimestampedModelSerializer):
    """
    Serializer for Comment model.
    """
    
    author = UserSerializer(read_only=True)
    comment_type_display = serializers.CharField(source='get_comment_type_display', read_only=True)
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Computed fields
    can_edit = serializers.SerializerMethodField()
    display_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = [
            'id', 'author', 'exchange', 'created_at', 'is_edited', 
            'edited_at', 'original_text', 'is_viewed_by_student', 'viewed_at'
        ]
    
    def get_can_edit(self, obj):
        """Check if current user can edit this comment."""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        # Authors can edit their own comments, staff can edit any
        return (obj.author == request.user or 
                request.user.is_staff or 
                hasattr(request.user, 'profile') and 
                hasattr(request.user.profile, 'is_staff_role') and 
                request.user.profile.is_staff_role())
    
    def get_display_text(self, obj):
        """Get the text to display (showing edit history if needed)."""
        if obj.is_edited and obj.original_text:
            return {
                'current': obj.text,
                'original': obj.original_text,
                'edited_at': obj.edited_at
            }
        return {'current': obj.text}
    
    def create(self, validated_data):
        """Create comment with current user as author and exchange from context."""
        validated_data['author'] = self.context['request'].user
        validated_data['exchange'] = self.context.get('exchange')
        return super().create(validated_data)
    
    def validate_comment_type(self, value):
        """Validate comment type based on user permissions."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        # Only staff can create internal comments
        if value == 'INTERNAL':
            if not request.user.is_staff:
                # Check if user has staff profile
                if not (hasattr(request.user, 'profile') and 
                       hasattr(request.user.profile, 'is_staff_role') and 
                       request.user.profile.is_staff_role()):
                    raise serializers.ValidationError("Only staff can create internal comments")
        
        # Only staff can create official communications
        if value == 'OFFICIAL':
            if not request.user.is_staff:
                if not (hasattr(request.user, 'profile') and 
                       hasattr(request.user.profile, 'is_staff_role') and 
                       request.user.profile.is_staff_role()):
                    raise serializers.ValidationError("Only staff can create official communications")
        
        return value


class CommentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing comments.
    """
    
    author = UserSerializer(read_only=True)
    comment_type_display = serializers.CharField(source='get_comment_type_display', read_only=True)
    preview_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'comment_type', 'comment_type_display',
            'preview_text', 'created_at', 'is_edited', 'is_viewed_by_student'
        ]
    
    def get_preview_text(self, obj):
        """Get preview of comment text (first 100 characters)."""
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    """
    
    class Meta:
        model = Comment
        fields = ['comment_type', 'text']
    
    def create(self, validated_data):
        """Create comment with context data."""
        validated_data['author'] = self.context['request'].user
        validated_data['exchange'] = self.context['exchange']
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating comments.
    """
    
    class Meta:
        model = Comment
        fields = ['text']
    
    def update(self, instance, validated_data):
        """Update comment using the edit method to preserve history."""
        new_text = validated_data.get('text')
        if new_text and new_text != instance.text:
            instance.edit(new_text)
        return instance


class ReviewSerializer(TimestampedModelSerializer):
    """
    Serializer for Review model.
    """
    
    reviewer = UserSerializer(read_only=True)
    exchange = serializers.PrimaryKeyRelatedField(read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    
    # Computed fields
    can_revise = serializers.SerializerMethodField()
    revision_history = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = [
            'id', 'reviewer', 'exchange', 'reviewed_at', 'is_revised', 
            'revised_at', 'revision_reason', 'previous_decision'
        ]
    
    def get_can_revise(self, obj):
        """Check if current user can revise this review."""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        
        # Only the reviewer or senior staff can revise
        return (obj.reviewer == request.user or 
                request.user.is_superuser)
    
    def get_revision_history(self, obj):
        """Get revision history if available."""
        if obj.is_revised:
            return {
                'previous_decision': obj.previous_decision,
                'revised_at': obj.revised_at,
                'revision_reason': obj.revision_reason
            }
        return None
    
    def create(self, validated_data):
        """Create review with current user as reviewer and exchange from context."""
        validated_data['reviewer'] = self.context['request'].user
        validated_data['exchange'] = self.context.get('exchange')
        return super().create(validated_data)
    
    def validate_review_type(self, value):
        """Validate review type based on user permissions."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        # Add specific validation based on review type if needed
        # For example, only financial staff can do financial reviews
        
        return value


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing reviews.
    """
    
    reviewer = UserSerializer(read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'review_type', 'review_type_display',
            'decision', 'decision_display', 'reviewed_at', 'is_revised'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reviews.
    """
    
    class Meta:
        model = Review
        fields = [
            'review_type', 'decision', 'comments', 'conditions'
        ]
    
    def create(self, validated_data):
        """Create review with context data."""
        validated_data['reviewer'] = self.context['request'].user
        validated_data['exchange'] = self.context['exchange']
        return super().create(validated_data)


class ReviewRevisionSerializer(serializers.Serializer):
    """
    Serializer for revising reviews.
    """
    
    new_decision = serializers.ChoiceField(
        choices=Review.DECISION_CHOICES,
        required=True,
        help_text="New decision for the review"
    )
    reason = serializers.CharField(
        required=True,
        help_text="Reason for the revision"
    )
    
    def validate_new_decision(self, value):
        """Validate that the new decision is different from current."""
        review = self.context.get('review')
        if review and value == review.decision:
            raise serializers.ValidationError("New decision must be different from current decision")
        return value


class CommentMarkViewedSerializer(serializers.Serializer):
    """
    Serializer for marking comments as viewed by student.
    """
    
    comment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of comment IDs to mark as viewed"
    )
    
    def validate_comment_ids(self, value):
        """Validate that all comment IDs exist and are visible to student."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        # Get comments that are visible to students
        visible_comments = Comment.objects.filter(
            id__in=value,
            comment_type__in=['STUDENT', 'OFFICIAL']
        )
        
        found_ids = set(visible_comments.values_list('id', flat=True))
        invalid_ids = set(value) - found_ids
        
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid or inaccessible comment IDs: {list(invalid_ids)}")
        
        return value
