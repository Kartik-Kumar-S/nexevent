# certificates/models.py
import uuid
import hashlib
import secrets
import datetime
from django.db import models
from django.conf import settings


class CertificateTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    CATEGORY_CHOICES = [
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('competition', 'Competition'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
    ]
    event_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    html_template = models.TextField()
    background_image = models.ImageField(
        upload_to='certificate_templates/backgrounds/', 
        blank=True, null=True
    )
    logo = models.ImageField(
        upload_to='certificate_templates/logos/', 
        blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.event_category})"


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    registration = models.OneToOneField(
        'registrations.Registration',
        on_delete=models.CASCADE,
        related_name='certificate'
    )
    template = models.ForeignKey(
        CertificateTemplate,
        on_delete=models.SET_NULL,
        null=True
    )

    certificate_number = models.CharField(max_length=50, unique=True, db_index=True)

    TYPE_CHOICES = [
        ('attendance', 'Attendance'),
        ('participation', 'Participation'),
        ('winner', 'Winner'),
        ('volunteer', 'Volunteer'),
    ]
    certificate_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='attendance'
    )

    pdf_file = models.FileField(
        upload_to='certificates/pdfs/%Y/%m/',
        blank=True, null=True
    )
    verification_qr = models.ImageField(
        upload_to='certificates/qr_codes/',
        blank=True, null=True
    )
    verification_url = models.URLField(blank=True)

    # Simple SHA-256 hash for tamper detection — no blockchain needed
    verification_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="SHA-256 hash for verification"
    )

    STATUS_CHOICES = [
        ('pending', 'Pending Generation'),
        ('generating', 'Generating'),
        ('generated', 'Generated'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='issued_certificates'
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoke_reason = models.TextField(blank=True)

    additional_data = models.JSONField(default=dict, blank=True)
    download_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['student', 'event', 'certificate_type']
        indexes = [
            models.Index(fields=['certificate_number']),
            models.Index(fields=['verification_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['student', 'status']),
        ]

    def __str__(self):
        return f"{self.certificate_number} - {self.student} - {self.event}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self._generate_certificate_number()
        if not self.verification_hash:
            self.verification_hash = self._generate_hash()
        super().save(*args, **kwargs)

    def _generate_certificate_number(self):
        year = datetime.date.today().year
        event_code = str(self.event_id)[:8].upper()
        random_part = secrets.token_hex(3).upper()
        return f"CERT-{year}-{event_code}-{random_part}"

    def _generate_hash(self):
        data = f"{self.id}{self.student_id}{self.event_id}{self.certificate_number}"
        return hashlib.sha256(data.encode()).hexdigest()