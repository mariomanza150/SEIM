"""API v1 views for exchange application."""

from rest_framework import viewsets, permissions
from ...models import Exchange, Document, Course, Comment, Timeline
from ...models.profiles.student_profile import StudentProfile
from .serializers import ExchangeSerializer, DocumentSerializer, UserProfileSerializer, CourseSerializer, CommentSerializer, TimelineSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ExchangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing exchange applications.
    list: Return a list of all exchanges
    create: Create a new exchange application
    retrieve: Get details of an exchange
    update: Update an exchange
    partial_update: Partially update an exchange
    destroy: Delete an exchange
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "destination_university", "exchange_program", "created_at"]
    search_fields = ["first_name", "last_name", "email", "student__username"]
    ordering_fields = ["created_at", "updated_at", "status"]

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing documents.
    list: Return a list of all documents
    create: Upload a new document
    retrieve: Get details of a document
    update: Update a document
    partial_update: Partially update a document
    destroy: Delete a document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "is_verified", "uploaded_at", "expires_at"]
    search_fields = ["original_filename", "description"]
    ordering_fields = ["uploaded_at", "modified_at", "is_verified"]

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses.
    list: Return a list of all courses
    create: Create a new course
    retrieve: Get details of a course
    update: Update a course
    partial_update: Partially update a course
    destroy: Delete a course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "code"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing comments.
    list: Return a list of all comments
    create: Create a new comment
    retrieve: Get details of a comment
    update: Update a comment
    partial_update: Partially update a comment
    destroy: Delete a comment
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["exchange", "created_at"]
    search_fields = ["text", "author__username"]
    ordering_fields = ["created_at"]

class TimelineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing timeline events.
    list: Return a list of all timeline events
    create: Create a new timeline event
    retrieve: Get details of a timeline event
    update: Update a timeline event
    partial_update: Partially update a timeline event
    destroy: Delete a timeline event
    """
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["exchange", "event_type", "created_at"]
    search_fields = ["event_type", "description"]
    ordering_fields = ["created_at"]

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user profiles.
    list: Return a list of all user profiles
    create: Create a new user profile
    retrieve: Get details of a user profile
    update: Update a user profile
    partial_update: Partially update a user profile
    destroy: Delete a user profile
    """
    queryset = StudentProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["institution", "department", "role", "is_verified"]
    search_fields = ["user__username", "user__email", "institution"]
    ordering_fields = ["user__username", "institution"]

# TODO: Implement CourseSerializer, CommentSerializer, TimelineSerializer and add them to the respective ViewSets above.
