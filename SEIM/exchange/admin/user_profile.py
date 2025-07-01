"""
Admin configuration for User Profile models.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.people.user_profile import UserProfile
from ..models.people.student_profile import StudentProfile
from ..models.people.staff_profile import StaffProfile
from ..models.people.contact_profile import ContactProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model (LEGACY - To be removed)"""

    list_display = ("user", "institution", "department", "student_id", "position")
    list_filter = ("institution", "department", "country")
    search_fields = ("user__username", "user__email", "institution", "student_id")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Personal Information"), {"fields": ("date_of_birth", "gender", "phone")}),
        (_("Contact Information"), {"fields": ("address", "city", "country")}),
        (_("Academic Information"), {"fields": ("student_id", "institution", "department", "current_program")}),
        (_("Staff Information"), {"fields": ("position", "office_phone")}),
        (_("System Information"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin interface for StudentProfile model"""

    list_display = (
        "user",
        "student_id",
        "university",
        "department",
        "current_semester",
        "is_active",
    )
    list_filter = ("is_active", "current_semester", "university", "department")
    search_fields = ("user__username", "user__email", "student_id", "department")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "date_of_birth",
                    "gender",
                    "phone_number",
                    "emergency_contact",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            _("Academic Information"),
            {
                "fields": (
                    "student_id",
                    "university",
                    "department",
                    "major",
                    "current_semester",
                    "academic_level",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "last_login",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin interface for StaffProfile model"""

    list_display = (
        "user",
        "staff_id",
        "university",
        "department",
        "position",
        "is_active",
    )
    list_filter = ("is_active", "position", "university", "department")
    search_fields = ("user__username", "user__email", "staff_id", "department")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "date_of_birth",
                    "gender",
                    "phone_number",
                    "emergency_contact",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            _("Staff Information"),
            {
                "fields": (
                    "staff_id",
                    "university",
                    "department",
                    "position",
                    "office_location",
                    "office_phone",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "last_login",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


@admin.register(ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    """Admin interface for ContactProfile model"""

    list_display = (
        "user",
        "university",
        "department",
        "position",
        "is_primary",
        "is_active",
    )
    list_filter = ("is_active", "is_primary", "university")
    search_fields = ("user__username", "user__email", "department", "position")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "date_of_birth",
                    "gender",
                    "phone_number",
                    "emergency_contact",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": (
                    "university",
                    "department",
                    "position",
                    "office_phone",
                    "mobile_phone",
                    "is_primary",
                )
            },
        ),
        (
            _("Availability"),
            {
                "fields": (
                    "availability_notes",
                    "preferred_contact_method",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "last_login",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
