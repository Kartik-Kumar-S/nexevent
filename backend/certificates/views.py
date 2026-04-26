from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Certificate, CertificateTemplate
from .serializers import CertificateTemplateSerializer, CertificateListSerializer, CertificateDetailSerializer

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for handling Certificates.
    """
    queryset = Certificate.objects.select_related('student', 'event').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CertificateListSerializer
        return CertificateDetailSerializer

    def get_permissions(self):
        if self.action == 'verify':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Certificate.objects.none()
        return self.queryset.filter(student=user) | self.queryset.filter(event__organizer=user)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.AllowAny],
            url_path='verify/(?P<hash>[a-f0-9]{64})')
    def verify(self, request, hash=None):
        """
        GET /api/certificates/verify/{sha256_hash}/
        """
        certificate = get_object_or_404(
            Certificate.objects.select_related('student', 'event'),
            verification_hash=hash
        )

        if certificate.status == 'revoked':
            return Response({
                'is_valid': False,
                'message': 'This certificate has been revoked.',
                'revoked_at': certificate.revoked_at,
            }, status=status.HTTP_200_OK)

        return Response({
            'is_valid': True,
            'certificate_number': certificate.certificate_number,
            'student_name': certificate.student.get_full_name(),
            'event_name': certificate.event.title,
            'event_date': certificate.event.date,
            'certificate_type': certificate.get_certificate_type_display(),
            'issued_at': certificate.issued_at,
        })

class CertificateTemplateViewSet(viewsets.ModelViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
