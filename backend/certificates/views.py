# In views.py verify action
@action(detail=False, methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='verify/(?P<hash>[a-f0-9]{64})')
def verify(self, request, hash=None):
    """
    GET /api/v1/certificates/verify/{sha256_hash}/
    Public — no auth needed. Anyone with QR can verify.
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