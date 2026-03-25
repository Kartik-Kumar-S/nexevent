
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    

    # ---- List View ----
    list_display = (
        'email', 'username', 'full_name',
        'role', 'is_verified', 'is_active', 'date_joined',
    )
    list_filter = ('role', 'is_verified', 'is_active', 'department')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'student_id')
    ordering = ('-date_joined',)

    # ---- Detail View ----
    # fieldsets controls the layout of the user edit page
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('username', 'first_name', 'last_name'),
        }),
        ('Campus Info', {
            'fields': ('student_id', 'department', 'year_of_study'),
        }),
        ('Role & Status', {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser'),
        }),
        ('Preferences', {
            'fields': ('notification_preferences',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    # ---- Create User Form ----
    # fieldsets for the "Add User" page in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'role',
            ),
        }),
    )