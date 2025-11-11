"""API views for grade translation system."""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import GradeScale, GradeTranslation, GradeValue
from .serializers import (
    BulkTranslationRequestSerializer,
    EligibilityCheckRequestSerializer,
    EligibilityCheckResponseSerializer,
    GPAConversionRequestSerializer,
    GradeScaleListSerializer,
    GradeScaleSerializer,
    GradeTranslationRequestSerializer,
    GradeTranslationResponseSerializer,
    GradeTranslationSerializer,
    GradeValueSerializer,
)
from .services import GradeTranslationService


class GradeScaleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing grade scales."""
    queryset = GradeScale.objects.prefetch_related('grade_values').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return GradeScaleListSerializer
        return GradeScaleSerializer

    @extend_schema(
        summary="List all grade scales",
        description="Get a list of all grade scales with basic information."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a grade scale",
        description="Get detailed information about a specific grade scale including all grade values."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Get active grade scales",
        description="Get only active grade scales."
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active grade scales."""
        active_scales = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_scales, many=True)
        return Response(serializer.data)


class GradeValueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing grade values."""
    queryset = GradeValue.objects.select_related('grade_scale').all()
    serializer_class = GradeValueSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all grade values",
        description="Get a list of all grade values across all scales."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get grade values for a scale",
        parameters=[
            OpenApiParameter(
                name='grade_scale',
                description='Grade scale ID',
                required=False,
                type=str
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_scale(self, request):
        """Get grade values filtered by scale."""
        scale_id = request.query_params.get('grade_scale')
        if scale_id:
            values = self.queryset.filter(grade_scale_id=scale_id)
        else:
            values = self.queryset.all()

        serializer = self.get_serializer(values, many=True)
        return Response(serializer.data)


class GradeTranslationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing grade translations."""
    queryset = GradeTranslation.objects.select_related(
        'source_grade', 'source_grade__grade_scale',
        'target_grade', 'target_grade__grade_scale',
        'created_by'
    ).all()
    serializer_class = GradeTranslationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Translate a grade",
        request=GradeTranslationRequestSerializer,
        responses={200: GradeTranslationResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def translate(self, request):
        """Translate a grade value to a target scale."""
        serializer = GradeTranslationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            source_grade = GradeValue.objects.select_related('grade_scale').get(
                id=serializer.validated_data['source_grade_value_id']
            )

            target_grade = GradeTranslationService.translate_grade(
                str(serializer.validated_data['source_grade_value_id']),
                str(serializer.validated_data['target_scale_id']),
                fallback_to_gpa=serializer.validated_data['fallback_to_gpa']
            )

            # Determine translation method
            if target_grade:
                # Check if direct translation exists
                direct_trans = GradeTranslation.objects.filter(
                    source_grade=source_grade,
                    target_grade=target_grade
                ).first()

                if direct_trans:
                    method = 'direct'
                    confidence = direct_trans.confidence
                else:
                    method = 'gpa_equivalent'
                    confidence = None
            else:
                method = 'not_found'
                confidence = None

            response_data = {
                'source_grade': GradeValueSerializer(source_grade).data,
                'target_grade': GradeValueSerializer(target_grade).data if target_grade else None,
                'translation_method': method,
                'confidence': confidence
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Convert GPA to grade scale",
        request=GPAConversionRequestSerializer,
        responses={200: GradeValueSerializer}
    )
    @action(detail=False, methods=['post'])
    def convert_gpa(self, request):
        """Convert a numeric GPA value to a grade in the target scale."""
        serializer = GPAConversionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            grade = GradeTranslationService.convert_gpa_to_scale(
                serializer.validated_data['gpa_value'],
                str(serializer.validated_data['target_scale_id'])
            )

            if grade:
                return Response(GradeValueSerializer(grade).data)
            else:
                return Response(
                    {'error': 'No matching grade found in target scale'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Check eligibility with grade translation",
        request=EligibilityCheckRequestSerializer,
        responses={200: EligibilityCheckResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def check_eligibility(self, request):
        """Check if student grade meets program requirement with translation."""
        serializer = EligibilityCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = GradeTranslationService.check_eligibility_with_translation(
                serializer.validated_data['student_gpa'],
                str(serializer.validated_data['student_scale_id']),
                serializer.validated_data['required_gpa'],
                str(serializer.validated_data['required_scale_id'])
            )

            return Response(result)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Create bulk translations",
        request=BulkTranslationRequestSerializer,
        responses={200: GradeTranslationSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple translations at once."""
        serializer = BulkTranslationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            translations = GradeTranslationService.bulk_create_translations(
                str(serializer.validated_data['source_scale_id']),
                str(serializer.validated_data['target_scale_id']),
                serializer.validated_data['mapping'],
                user=request.user
            )

            return Response(
                GradeTranslationSerializer(translations, many=True).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
