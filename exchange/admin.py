from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from accounts.models import User
from documents.models import ExchangeAgreementDocument

from .agreement_renewal import AgreementRenewalService
from .models import (
    AgreementExpirationReminderLog,
    Application,
    ApplicationStatus,
    Comment,
    ExchangeAgreement,
    Program,
    SavedSearch,
    TimelineEvent,
)


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


@admin.register(AgreementExpirationReminderLog)
class AgreementExpirationReminderLogAdmin(admin.ModelAdmin):
    list_display = ("agreement", "days_before", "agreement_end_date", "created_at")
    list_filter = ("days_before",)
    search_fields = ("agreement__title", "agreement__partner_institution_name")
    readonly_fields = ("agreement", "days_before", "agreement_end_date", "created_at", "updated_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ExchangeAgreementDocumentInline(admin.TabularInline):
    model = ExchangeAgreementDocument
    extra = 0
    fields = ("category", "title", "file", "supersedes", "notes", "uploaded_by", "created_at")
    readonly_fields = ("uploaded_by", "created_at")
    raw_id_fields = ("supersedes",)


@admin.register(ExchangeAgreement)
class ExchangeAgreementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "partner_institution_name",
        "partner_country",
        "agreement_type",
        "status",
        "start_date",
        "end_date",
        "program_summary",
    )
    list_filter = ("status", "agreement_type")
    search_fields = (
        "title",
        "partner_institution_name",
        "internal_reference",
        "partner_reference_id",
        "notes",
    )
    filter_horizontal = ("programs",)
    readonly_fields = ("created_at", "updated_at")
    actions = (
        "mark_expired_by_date",
        "mark_active",
        "admin_mark_renewal_pending",
        "admin_create_renewal_successor",
    )
    inlines = (ExchangeAgreementDocumentInline,)

    fieldsets = (
        (None, {"fields": ("title", "status", "agreement_type")}),
        (
            "Partner",
            {"fields": ("partner_institution_name", "partner_country", "partner_reference_id")},
        ),
        ("Coverage", {"fields": ("programs",)}),
        ("Dates", {"fields": ("start_date", "end_date")}),
        (
            "Renewal",
            {
                "fields": ("renewed_from", "renewal_follow_up_due"),
                "description": "Link to predecessor when this record supersedes another; follow-up date for renewal tasks.",
            },
        ),
        ("Internal", {"fields": ("internal_reference", "notes")}),
        ("Audit", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def program_summary(self, obj):
        count = obj.programs.count()
        if not count:
            return format_html('<span style="color:#999;">—</span>')
        return f"{count} program(s)"

    program_summary.short_description = "Programs"

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, ExchangeAgreementDocument) and not instance.uploaded_by_id:
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()

    @admin.action(description="Mark as expired (where end date is before today)")
    def mark_expired_by_date(self, request, queryset):
        from django.utils import timezone

        today = timezone.localdate()
        qs = queryset.filter(end_date__lt=today).exclude(status=ExchangeAgreement.Status.EXPIRED)
        updated = qs.update(status=ExchangeAgreement.Status.EXPIRED)
        self.message_user(
            request,
            f"Marked {updated} agreement(s) as expired.",
            messages.SUCCESS,
        )

    @admin.action(description="Set status to Active")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=ExchangeAgreement.Status.ACTIVE)
        self.message_user(
            request,
            f"Set {updated} agreement(s) to Active.",
            messages.SUCCESS,
        )

    @admin.action(description="Mark renewal pending (workflow)")
    def admin_mark_renewal_pending(self, request, queryset):
        ok = 0
        for ag in queryset:
            try:
                AgreementRenewalService.mark_renewal_pending(ag, notify=True)
                ok += 1
            except ValueError as exc:
                self.message_user(request, f"{ag}: {exc}", messages.WARNING)
        if ok:
            self.message_user(
                request,
                f"Marked {ok} agreement(s) renewal pending.",
                messages.SUCCESS,
            )

    @admin.action(description="Create renewal draft successor (+ rollover documents)")
    def admin_create_renewal_successor(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Select exactly one agreement to create a renewal successor.",
                messages.ERROR,
            )
            return
        ag = queryset.first()
        try:
            successor = AgreementRenewalService.create_renewal_successor(
                ag, request.user, copy_documents=True
            )
        except ValueError as exc:
            self.message_user(request, str(exc), messages.ERROR)
            return
        url = reverse("admin:exchange_exchangeagreement_change", args=[successor.pk])
        self.message_user(
            request,
            format_html('Created renewal draft: <a href="{}">{}</a>', url, successor.title),
            messages.SUCCESS,
        )


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "application_window_summary",
        "coordinator_summary",
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
    readonly_fields = (
        "created_at",
        "updated_at",
        "application_count",
        "cms_program_page_summary",
    )
    actions = [
        "clone_programs",
        "activate_programs",
        "deactivate_programs",
        "create_draft_cms_program_pages",
        "sync_operational_data_to_cms_pages",
    ]

    filter_horizontal = ("required_document_types",)

    fieldsets = (
        (None, {
            "fields": ("name", "description", "is_active", "recurring")
        }),
        ("Dates", {
            "fields": ("application_open_date", "application_deadline", "start_date", "end_date")
        }),
        ("Enrollment", {
            "fields": ("enrollment_capacity", "waitlist_when_full"),
            "description": "Optional seat limit; waitlist applies when full and enabled.",
        }),
        ("Academic Requirements", {
            "fields": ("min_gpa", "application_form", "coordinators", "required_document_types"),
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
            "fields": (
                "created_at",
                "updated_at",
                "application_count",
                "cms_program_page_summary",
            ),
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

    def application_window_summary(self, obj):
        """Display application window status in the changelist."""
        if not obj.application_open_date and not obj.application_deadline:
            return format_html('<span style="color: #999;">Always open</span>')

        status = obj.get_application_window_status()
        color = "#198754" if status["is_open"] else "#dc3545"
        return format_html('<span style="color: {}; font-size: 0.9em;">{}</span>', color, status["message"])

    application_window_summary.short_description = "Application Window"

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

    def coordinator_summary(self, obj):
        coordinators = list(obj.coordinators.all()[:3])
        if not coordinators:
            return format_html('<span style="color: #999;">Unassigned</span>')

        names = [coordinator.get_full_name().strip() or coordinator.username for coordinator in coordinators]
        extra_count = obj.coordinators.count() - len(names)
        if extra_count > 0:
            names.append(f"+{extra_count} more")
        return ", ".join(names)

    coordinator_summary.short_description = "Coordinators"

    def cms_program_page_summary(self, obj):
        if not obj.pk:
            return "—"
        from cms.models import ProgramPage

        page = ProgramPage.objects.filter(program=obj).first()
        if not page:
            return format_html(
                '<span style="color:#666;">No linked CMS page. Use the list action '
                "<strong>Create draft CMS program page</strong> or link one in Wagtail.</span>"
            )
        edit_url = reverse("wagtailadmin_pages:edit", args=[page.id])
        status = "Live" if page.live else "Draft"
        return format_html(
            '<a href="{}">Edit in Wagtail</a> <span style="color:#666;">({})</span>',
            edit_url,
            status,
        )

    cms_program_page_summary.short_description = "Public program page (CMS)"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "coordinators":
            kwargs["queryset"] = User.objects.filter(roles__name="coordinator").distinct().order_by("username")
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @admin.action(description="🔄 Clone selected programs")
    def clone_programs(self, request, queryset):
        """Clone selected programs with (Copy) suffix."""
        cloned_count = 0
        for program in queryset:
            cloned_program = Program.objects.create(
                name=f"{program.name} (Copy)",
                description=program.description,
                start_date=program.start_date,
                end_date=program.end_date,
                application_open_date=program.application_open_date,
                application_deadline=program.application_deadline,
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
            cloned_program.coordinators.set(program.coordinators.all())
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

    @admin.action(description="📄 Create draft CMS program page (linked to program index)")
    def create_draft_cms_program_pages(self, request, queryset):
        from cms.exchange_program_sync import create_draft_program_page_for_program
        from cms.models import ProgramPage

        created = 0
        skipped = 0
        errors = []
        for program in queryset:
            if ProgramPage.objects.filter(program=program).exists():
                skipped += 1
                continue
            try:
                create_draft_program_page_for_program(program, user=request.user)
                created += 1
            except ValueError as exc:
                errors.append(f"{program.name}: {exc}")
            except Exception as exc:
                errors.append(f"{program.name}: {exc}")

        if created:
            self.message_user(
                request,
                f"Created {created} draft CMS program page(s). Open Wagtail to edit body and publish.",
                messages.SUCCESS,
            )
        if skipped:
            self.message_user(
                request,
                f"Skipped {skipped} program(s) that already have a linked CMS page.",
                messages.WARNING,
            )
        if errors:
            self.message_user(request, "Errors: " + "; ".join(errors), messages.ERROR)

    @admin.action(description="🔁 Sync operational data to linked CMS program pages")
    def sync_operational_data_to_cms_pages(self, request, queryset):
        from cms.exchange_program_sync import sync_program_page_operational_fields_and_publish

        updated = 0
        missing = 0
        for program in queryset:
            status, _ = sync_program_page_operational_fields_and_publish(
                program, user=request.user
            )
            if status == "updated":
                updated += 1
            else:
                missing += 1

        if updated:
            self.message_user(
                request,
                f"Updated {updated} linked CMS program page(s). Live pages were re-published.",
                messages.SUCCESS,
            )
        if missing:
            self.message_user(
                request,
                f"{missing} program(s) have no linked CMS page (use create draft first).",
                messages.WARNING,
            )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "program",
        "assigned_coordinator",
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
            "fields": ("program", "student", "assigned_coordinator", "status", "withdrawn")
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_coordinator":
            kwargs["queryset"] = User.objects.filter(roles__name="coordinator").distinct().order_by("username")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
