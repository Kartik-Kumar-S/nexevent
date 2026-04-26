from django.contrib import admin
from .models import Certificate, CertificateTemplate

@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_category', 'is_active', 'created_at')
    list_filter = ('event_category', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'event', 'certificate_type', 'status', 'issued_at')
    list_filter = ('status', 'certificate_type', 'issued_at')
    search_fields = ('certificate_number', 'student__email', 'event__title')
    readonly_fields = ('id', 'certificate_number', 'verification_hash', 'created_at')
