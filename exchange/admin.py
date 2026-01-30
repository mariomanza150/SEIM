from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Application, ApplicationStatus, Comment, Program, SavedSearch, TimelineEvent


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "text", "is_private", "created_at")
    readonly_fields = ("created_at",)


class TimelineEventInline(admin.TabularInline):
    model = TimelineEvent
    extra = 0
    fields = ("event_type", "description", "created_by", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_active",
        "eligibility_summary",
        "application_count",
    )
    search_fields = ("name", "description")
    list_filter = (
        "is_active",
        "recurring",
        "auto_reject_ineligible",
        "required_language",
        "min_language_level",
    )
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "application_count")
    actions = ["clone_programs", "activate_programs", "deactivate_programs"]

    fieldsets = (
        (None, {
            "fields": ("name", "description", "is_active", "recurring")
        }),
        ("Dates", {
            "fields": ("start_date", "end_date")
        }),
        ("Academic Requirements", {
            "fields": ("min_gpa", "application_form"),
            "description": "Academic eligibility criteria for applicants"
        }),
        ("Language Requirements", {
            "fields": ("required_language", "min_language_level"),
            "description": "Language proficiency requirements (CEFR scale: A1-C2)",
            "classes": ("collapse",)
        }),
        ("Age Requirements", {
            "fields": ("min_age", "max_age"),
            "description": "Age range requirements for applicants",
            "classes": ("collapse",)
        }),
        ("Automation", {
            "fields": ("auto_reject_ineligible",),
            "description": "Automatically reject applications that don't meet eligibility criteria",
            "classes": ("collapse",)
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at", "application_count"),
            "classes": ("collapse",)
        }),
    )

    def eligibility_summary(self, obj):
        """Display eligibility criteria summary with icons."""
        criteria = []

        if obj.min_gpa:
            criteria.append(f'📊 GPA ≥{obj.min_gpa}')

        if obj.required_language:
            lang_display = obj.required_language
            if obj.min_language_level:
                lang_display += f' ({obj.min_language_level}+)'
            criteria.append(f'🗣️ {lang_display}')

        if obj.min_age or obj.max_age:
            if obj.min_age and obj.max_age:
                criteria.append(f'🎂 {obj.min_age}-{obj.max_age} years')
            elif obj.min_age:
                criteria.append(f'🎂 {obj.min_age}+ years')
            elif obj.max_age:
                criteria.append(f'🎂 ≤{obj.max_age} years')

        if criteria:
            summary = ' | '.join(criteria)
            if obj.auto_reject_ineligible:
                summary += ' ⚡'
            return format_html('<span style="font-size: 0.9em;">{}</span>', summary)
        return format_html('<span style="color: #999;">No criteria</span>')

    eligibility_summary.short_description = "Eligibility Criteria"

    def application_count(self, obj):
        """Show number of applications for this program."""
        count = obj.application_set.count()
        if count > 0:
            return format_html(
                '<a href="/admin/exchange/application/?program__id__exact={}">{} application{}</a>',
                obj.id,
                count,
                's' if count != 1 else ''
            )
        return '0 applications'

    application_count.short_description = "Applications"

    @admin.action(description="🔄 Clone selected programs")
    def clone_programs(self, request, queryset):
        """Clone selected programs with (Copy) suffix."""
        cloned_count = 0
        for program in queryset:
            # Create clone
            Program.objects.create(
                name=f"{program.name} (Copy)",
                description=program.description,
                start_date=program.start_date,
                end_date=program.end_date,
                is_active=False,  # Clones start inactive
                min_gpa=program.min_gpa,
                required_language=program.required_language,
                min_language_level=program.min_language_level,
                min_age=program.min_age,
                max_age=program.max_age,
                auto_reject_ineligible=program.auto_reject_ineligible,
                recurring=program.recurring,
                application_form=program.application_form,
            )
            cloned_count += 1

        self.message_user(
            request,
            f"Successfully cloned {cloned_count} program{'s' if cloned_count != 1 else ''}. "
            f"Clones are inactive by default.",
            messages.SUCCESS
        )

    @admin.action(description="✅ Activate selected programs")
    def activate_programs(self, request, queryset):
        """Activate selected programs."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} program{'s' if updated != 1 else ''}.",
            messages.SUCCESS
        )

    @admin.action(description="❌ Deactivate selected programs")
    def deactivate_programs(self, request, queryset):
        """Deactivate selected programs."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} program{'s' if updated != 1 else ''}.",
            messages.SUCCESS
        )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "program",
        "status",
        "eligibility_status",
        "submitted_at",
        "withdrawn"
    )
    search_fields = ("id", "student__email", "student__username", "program__name")
    list_filter = ("status", "withdrawn", "program__required_language")
    list_editable = ("withdrawn",)
    readonly_fields = ("created_at", "updated_at", "submitted_at", "eligibility_check_details")
    actions = ["check_eligibility", "mark_as_withdrawn"]

    fieldsets = (
        (None, {
            "fields": ("program", "student", "status", "withdrawn")
        }),
        ("Eligibility", {
            "fields": ("eligibility_check_details",),
            "description": "Automatic eligibility validation results"
        }),
        ("Submission", {
            "fields": ("submitted_at",)
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    inlines = [CommentInline, TimelineEventInline]

    def eligibility_status(self, obj):
        """Show eligibility status with visual indicator."""
        try:
            from exchange.services import ApplicationService
            result = ApplicationService.check_eligibility(obj.student, obj.program)
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Eligible</span>'
            )
        except ValueError as e:
            error_msg = str(e).replace('Eligibility requirements not met:\n- ', '')
            return format_html(
                '<span style="color: red;" title="{}">✗ Ineligible</span>',
                error_msg
            )
        except Exception:
            return format_html('<span style="color: gray;">? Unknown</span>')

    eligibility_status.short_description = "Eligibility"

    def eligibility_check_details(self, obj):
        """Display detailed eligibility check results."""
        try:
            from exchange.services import ApplicationService
            result = ApplicationService.check_eligibility(obj.student, obj.program)

            html = '<div style="padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;">'
            html += '<strong style="color: #155724;">✓ Student meets all eligibility requirements</strong><br><br>'
            html += '<ul style="margin: 0; padding-left: 20px;">'

            profile = obj.student.profile
            if obj.program.min_gpa:
                html += f'<li>GPA: {profile.gpa} (required: ≥{obj.program.min_gpa})</li>'
            if obj.program.required_language:
                html += f'<li>Language: {profile.language} (required: {obj.program.required_language})</li>'
            if obj.program.min_language_level:
                html += f'<li>Language Level: {profile.language_level} (required: {obj.program.min_language_level}+)</li>'
            if obj.program.min_age or obj.program.max_age:
                from datetime import date
                dob = profile.date_of_birth
                if dob:
                    age = date.today().year - dob.year
                    html += f'<li>Age: {age} years'
                    if obj.program.min_age and obj.program.max_age:
                        html += f' (required: {obj.program.min_age}-{obj.program.max_age})'
                    elif obj.program.min_age:
                        html += f' (required: {obj.program.min_age}+)'
                    elif obj.program.max_age:
                        html += f' (required: ≤{obj.program.max_age})'
                    html += '</li>'

            html += '</ul></div>'
            return format_html(html)

        except ValueError as e:
            error_msg = str(e)
            html = '<div style="padding: 10px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px;">'
            html += '<strong style="color: #721c24;">✗ Student does not meet eligibility requirements</strong><br><br>'
            html += '<div style="color: #721c24; white-space: pre-line;">' + error_msg + '</div>'
            html += '</div>'
            return format_html(html)

        except Exception as e:
            return format_html(
                '<div style="padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">'
                '<strong>Unable to check eligibility:</strong> {}</div>',
                str(e)
            )

    eligibility_check_details.short_description = "Eligibility Details"

    @admin.action(description="🔍 Check eligibility for selected applications")
    def check_eligibility(self, request, queryset):
        """Check eligibility for selected applications."""
        eligible_count = 0
        ineligible_count = 0

        for application in queryset:
            try:
                from exchange.services import ApplicationService
                ApplicationService.check_eligibility(application.student, application.program)
                eligible_count += 1
            except ValueError:
                ineligible_count += 1

        self.message_user(
            request,
            f"Eligibility check complete: {eligible_count} eligible, {ineligible_count} ineligible",
            messages.INFO
        )

    @admin.action(description="🚫 Mark selected as withdrawn")
    def mark_as_withdrawn(self, request, queryset):
        """Mark selected applications as withdrawn."""
        updated = queryset.update(withdrawn=True)
        self.message_user(
            request,
            f"Successfully marked {updated} application{'s' if updated != 1 else ''} as withdrawn.",
            messages.SUCCESS
        )


@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)
    readonly_fields = ("id",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("application", "author", "is_private", "created_at")
    search_fields = ("application__id", "author__email", "text")
    list_filter = ("is_private",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ("application", "event_type", "created_by", "created_at")
    search_fields = ("application__id", "event_type", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    """Admin interface for SavedSearch model."""
    
    list_display = ("name", "user", "search_type", "is_default", "filter_count", "created_at")
    search_fields = ("name", "user__username", "user__email")
    list_filter = ("search_type", "is_default", "created_at")
    readonly_fields = ("created_at", "updated_at", "filter_preview")
    
    fieldsets = (
        (None, {
            "fields": ("user", "name", "search_type", "is_default")
        }),
        ("Filters", {
            "fields": ("filters", "filter_preview"),
            "description": "JSON filter parameters"
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def filter_count(self, obj):
        """Show number of filters applied."""
        count = len(obj.filters)
        return format_html(
            '<span class="badge" style="background: #0d6efd;">{} filter{}</span>',
            count,
            's' if count != 1 else ''
        )
    
    filter_count.short_description = "Filters"
    
    def filter_preview(self, obj):
        """Show preview of filter parameters."""
        import json
        filters_json = json.dumps(obj.filters, indent=2)
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
            filters_json
        )
    
    filter_preview.short_description = "Filter Parameters"
