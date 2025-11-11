"""Django admin configuration for grade translation system."""
from django.contrib import admin
from django.utils.html import format_html

from .models import GradeScale, GradeTranslation, GradeValue


class GradeValueInline(admin.TabularInline):
    """Inline admin for grade values within a grade scale."""
    model = GradeValue
    extra = 1
    fields = ['label', 'numeric_value', 'gpa_equivalent', 'min_percentage',
              'max_percentage', 'is_passing', 'order', 'description']
    ordering = ['order', 'numeric_value']


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    """Admin interface for grade scales."""
    list_display = [
        'name', 'code', 'country', 'value_range', 'passing_value',
        'is_reverse_scale', 'is_active', 'grade_count'
    ]
    list_filter = ['is_active', 'is_reverse_scale', 'country']
    search_fields = ['name', 'code', 'description', 'country']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'country')
        }),
        ('Scale Configuration', {
            'fields': ('min_value', 'max_value', 'passing_value', 'is_reverse_scale')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [GradeValueInline]

    def value_range(self, obj):
        """Display the value range of the scale."""
        return f"{obj.min_value} - {obj.max_value}"
    value_range.short_description = 'Value Range'

    def grade_count(self, obj):
        """Display the number of grade values in this scale."""
        count = obj.grade_values.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span> grades',
            count
        )
    grade_count.short_description = 'Grade Values'


@admin.register(GradeValue)
class GradeValueAdmin(admin.ModelAdmin):
    """Admin interface for individual grade values."""
    list_display = [
        'label', 'grade_scale', 'numeric_value', 'gpa_equivalent',
        'percentage_range', 'is_passing', 'translation_count'
    ]
    list_filter = ['grade_scale', 'is_passing']
    search_fields = ['label', 'description', 'grade_scale__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Grade Information', {
            'fields': ('grade_scale', 'label', 'description', 'order')
        }),
        ('Numeric Values', {
            'fields': ('numeric_value', 'gpa_equivalent')
        }),
        ('Percentage Range (Optional)', {
            'fields': ('min_percentage', 'max_percentage'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_passing',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['grade_scale', 'order']

    def percentage_range(self, obj):
        """Display percentage range if available."""
        if obj.min_percentage is not None and obj.max_percentage is not None:
            return f"{obj.min_percentage}% - {obj.max_percentage}%"
        return "Not specified"
    percentage_range.short_description = 'Percentage Range'

    def translation_count(self, obj):
        """Display number of translations for this grade."""
        from_count = obj.translations_from.count()
        to_count = obj.translations_to.count()
        return format_html(
            '<span title="Translations from this grade">{}</span> / '
            '<span title="Translations to this grade">{}</span>',
            from_count, to_count
        )
    translation_count.short_description = 'Translations (From/To)'


@admin.register(GradeTranslation)
class GradeTranslationAdmin(admin.ModelAdmin):
    """Admin interface for grade translations."""
    list_display = [
        'source_info', 'target_info', 'confidence_display',
        'gpa_difference', 'created_by', 'created_at'
    ]
    list_filter = [
        'source_grade__grade_scale',
        'target_grade__grade_scale',
        'created_at'
    ]
    search_fields = [
        'source_grade__label',
        'target_grade__label',
        'source_grade__grade_scale__name',
        'target_grade__grade_scale__name',
        'notes'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'gpa_difference']
    fieldsets = (
        ('Translation Mapping', {
            'fields': ('source_grade', 'target_grade')
        }),
        ('Translation Details', {
            'fields': ('confidence', 'notes', 'created_by')
        }),
        ('GPA Analysis', {
            'fields': ('gpa_difference',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ['source_grade', 'target_grade', 'created_by']

    def source_info(self, obj):
        """Display source grade information."""
        return format_html(
            '<strong>{}</strong> ({})<br><small>GPA: {:.2f}</small>',
            obj.source_grade.label,
            obj.source_grade.grade_scale.code,
            obj.source_grade.gpa_equivalent
        )
    source_info.short_description = 'Source Grade'

    def target_info(self, obj):
        """Display target grade information."""
        return format_html(
            '<strong>{}</strong> ({})<br><small>GPA: {:.2f}</small>',
            obj.target_grade.label,
            obj.target_grade.grade_scale.code,
            obj.target_grade.gpa_equivalent
        )
    target_info.short_description = 'Target Grade'

    def confidence_display(self, obj):
        """Display confidence with visual indicator."""
        percentage = obj.confidence * 100
        if percentage >= 80:
            color = 'green'
        elif percentage >= 60:
            color = 'orange'
        else:
            color = 'red'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f}%</span>',
            color, percentage
        )
    confidence_display.short_description = 'Confidence'

    def gpa_difference(self, obj):
        """Display GPA difference between source and target."""
        diff = abs(obj.source_grade.gpa_equivalent - obj.target_grade.gpa_equivalent)
        return format_html(
            '<span title="Absolute difference in GPA equivalents">{:.3f}</span>',
            diff
        )
    gpa_difference.short_description = 'GPA Difference'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'source_grade',
            'source_grade__grade_scale',
            'target_grade',
            'target_grade__grade_scale',
            'created_by'
        )


# Customize admin site header
admin.site.site_header = "SEIM Grade Translation Administration"
admin.site.site_title = "SEIM Admin"
admin.site.index_title = "Grade Translation Management"
