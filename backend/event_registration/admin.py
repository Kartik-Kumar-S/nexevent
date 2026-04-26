from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "event",
        "status",
        "registered_at",
        "cancelled_at",
        "checked_in_at",
    )

    list_filter = (
        "status",
        "event",
        "registered_at",
    )

    search_fields = (
        "student__email",
        "student__username",
        "event__title",
    )

    readonly_fields = (
        "registered_at",
        "cancelled_at",
        "checked_in_at",
    )