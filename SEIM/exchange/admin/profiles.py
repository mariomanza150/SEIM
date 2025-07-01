from django.contrib import admin
from ..models import StudentProfile, StaffProfile, ContactProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'university',
        'student_id', 'institution', 'degree', 'academic_level',
        'country', 'is_verified', 'verification_date'
    )
    list_filter = (
        'university', 'academic_level', 'gender', 'country', 'is_verified',
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 'middle_name',
        'last_mothers_name', 'student_id', 'institution', 'degree',
        'city', 'country', 'university__name'
    )
    autocomplete_fields = ('university', 'groups', 'user_permissions')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'middle_name', 'last_name', 'last_mothers_name',
                'email', 'gender', 'date_of_birth',
            )
        }),
        ('Contact Info', {
            'fields': ('phone', 'address', 'city', 'country')
        }),
        ('Academic Info', {
            'fields': (
                'student_id', 'university', 'institution',
                'degree', 'academic_level'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers, or students to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if request.user.groups.filter(name="Students").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all; students see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.filter(username=request.user.username)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'university', 'role', 'position', 'is_verified', 'verification_date',
        'is_staff', 'is_superuser'
    )
    list_filter = (
        'role', 'is_verified', 'university', 'is_staff', 'is_superuser',
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name',
        'university__name', 'position'
    )
    autocomplete_fields = ('university', 'groups', 'user_permissions')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Profile details', {
            'fields': ('role', 'position', 'office_phone', 'university', 'is_verified', 'verification_date')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "username"):
            return obj.username == request.user.username
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all; staff see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.filter(username=request.user.username)


@admin.register(ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    list_display = (
        "university",
        "position",
        "phone",
        "office_phone",
        "city",
        "country",
    )
    list_filter = ("university", "country")
    search_fields = ("position", "phone", "office_phone", "address", "city", "country")
    autocomplete_fields = ("university",)

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        # No direct user ownership, so default to staff/manager only
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.none()

