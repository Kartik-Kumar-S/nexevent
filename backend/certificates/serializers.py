# certificates/serializers.py
from rest_framework import serializers
from .models import Certificate, CertificateTemplate


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = [
            'id', 'name', 'event_category', 'html_template',
            'background_image', 'logo', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CertificateListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    event_name = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'certificate_type',
            'student_name', 'event_name', 'status',
            'issued_at', 'created_at'
        ]


class CertificateDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    event_name = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateField(source='event.date', read_only=True)
    download_url = serializers.SerializerMethodField()
    verify_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'certificate_type',
            'student_name', 'student_email',
            'event_name', 'event_date',
            'status', 'pdf_file', 'download_url',
            'verify_url', 'verification_qr',
            'issued_at', 'download_count',
            'additional_data', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'certificate_number', 'verification_hash',
            'pdf_file', 'verification_qr',
            'download_count', 'created_at', 'updated_at'
        ]

    def get_download_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.pdf_file.url) if request else obj.pdf_file.url
        return None

    def get_verify_url(self, obj):
        return f"/api/v1/certificates/verify/{obj.verification_hash}/"


class CertificateBulkIssueSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    certificate_type = serializers.ChoiceField(
        choices=Certificate.TYPE_CHOICES,
        default='attendance'
    )
    template_id = serializers.UUIDField(required=False)
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="If empty, issues to ALL checked-in students"
    )

    def validate_event_id(self, value):
        from events.models import Event
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found.")
        if event.status != 'completed':
            raise serializers.ValidationError(
                "Certificates can only be issued for completed events."
            )
        return value