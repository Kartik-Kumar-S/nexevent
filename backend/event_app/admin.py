from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'organizer',
        'date',
        'time',
        'location',
        'category',
        'status',
    )
    list_filter = ('category', 'status', 'date')
    search_fields = ('title', 'location', 'organizer__email')
