import logging
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_certificate_task(self, certificate_id: str):
    """Generate PDF + QR for a single certificate."""
    from .models import Certificate
    from .services.certificate_generator import CertificateGeneratorService
    from .services.qr_service import QRService

    try:
        certificate = Certificate.objects.select_related(
            'student', 'event', 'template', 'event__organizer'
        ).get(id=certificate_id)

        certificate.status = 'generating'
        certificate.save(update_fields=['status'])

        # 1. Generate PDF
        generator = CertificateGeneratorService()
        pdf_buffer = generator.generate_pdf(certificate)

        filename = f"{certificate.certificate_number}.pdf"
        certificate.pdf_file.save(filename, ContentFile(pdf_buffer.read()), save=False)

        # 2. Generate verification QR
        qr_service = QRService()
        qr_buffer = qr_service.generate_verification_qr(certificate)

        qr_filename = f"qr_{certificate.certificate_number}.png"
        certificate.verification_qr.save(
            qr_filename, ContentFile(qr_buffer.read()), save=False
        )

        # 3. Update status
        certificate.status = 'generated'
        certificate.save(update_fields=[
            'pdf_file', 'verification_qr', 'status', 'updated_at'
        ])

        logger.info(f"Certificate generated: {certificate.certificate_number}")
        
        # 4. Trigger notification
        send_certificate_notification.delay(str(certificate.id))

        return {'status': 'success', 'certificate_id': str(certificate.id)}

    except Certificate.DoesNotExist:
        logger.error(f"Certificate {certificate_id} not found")
        return {'status': 'error', 'message': 'Certificate not found'}
    except Exception as exc:
        logger.error(f"Certificate generation failed: {exc}")
        Certificate.objects.filter(id=certificate_id).update(status='failed')
        raise self.retry(exc=exc)


@shared_task
def bulk_generate_certificates_task(event_id: str, certificate_type: str,
                                     template_id: str = None,
                                     student_ids: list = None):
    """
    Bulk issue certificates for all checked-in students of an event.
    Called by organizer after event completion.
    """
    from event_app.models import Event
    from event_registration.models import Registration
    from .models import Certificate, CertificateTemplate

    event = Event.objects.get(id=event_id)
    
    # Get template
    template = None
    if template_id:
        template = CertificateTemplate.objects.get(id=template_id)

    # Get eligible students (checked-in attendees)
    registrations = Registration.objects.filter(
        event=event,
        is_checked_in=True  # Only checked-in students get certificates
    ).select_related('student')

    if student_ids:
        registrations = registrations.filter(student_id__in=student_ids)

    created_count = 0
    for reg in registrations:
        # Skip if certificate already exists
        if Certificate.objects.filter(
            student=reg.student,
            event=event,
            certificate_type=certificate_type
        ).exists():
            continue

        cert = Certificate.objects.create(
            student=reg.student,
            event=event,
            registration=reg,
            template=template,
            certificate_type=certificate_type,
            status='pending'
        )

        # Queue individual generation
        generate_certificate_task.delay(str(cert.id))
        created_count += 1

    logger.info(
        f"Bulk certificate creation: {created_count} certificates "
        f"queued for event {event.title}"
    )
    return {'created': created_count, 'event_id': event_id}


@shared_task
def send_certificate_notification(certificate_id: str):
    """Notify student that their certificate is ready."""
    from .models import Certificate
    # Hook into your notification app
    certificate = Certificate.objects.select_related('student', 'event').get(
        id=certificate_id
    )
    
    certificate.status = 'issued'
    certificate.issued_at = timezone.now()
    certificate.save(update_fields=['status', 'issued_at'])
    
    # Example: trigger notification system
    # from notifications.services import NotificationService
    # NotificationService.send(
    #     user=certificate.student,
    #     trigger='certificate_issued',
    #     context={'certificate': certificate}
    # )
    logger.info(f"Certificate issued notification sent: {certificate.certificate_number}")
