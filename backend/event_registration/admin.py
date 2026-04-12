from django.contrib import admin
from .models import Registration, WaitlistEntry

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at']
    search_fields = ['student__username', 'event__title']

@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'position', 'added_at']
    list_filter = ['added_at']

