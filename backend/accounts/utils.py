import logging
from django.utils import timezone
from rest_framework.views import exception_handler
from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework import status
from .models import AuditLog

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Extract client IP from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(request, user, action, entity_type='', entity_id=None):
    """Helper to log audit actions with IP and User-Agent."""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # User could be AnonymousUser if unauthenticated, so check if it's a model instance
        if not user or not hasattr(user, 'id'):
            user = None

        AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            device=user_agent
        )
    except Exception as e:
        # We don't want audit logging to break the main request
        logger.error(f"Failed to create audit log: {str(e)}")

def custom_exception_handler(exc, context):
    """
    Custom exception handler to catch Ratelimited and return 429.
    """
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)
    return response
