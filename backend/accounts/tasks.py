import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_email_task(self, subject, message, recipient_list, html_message=None):
    """
    Celery task to send emails asynchronously.
    """
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nexevent.com')
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email '{subject}' sent to {recipient_list}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send email to {recipient_list}: {str(exc)}")
        raise self.retry(exc=exc)
