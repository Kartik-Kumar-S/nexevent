from uuid import UUID
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket


@api_view(["POST"])
@permission_classes([IsAdminUser])  
def check_in(request):

    ticket_id = request.data.get("ticket_id")

    if not ticket_id:
        return Response(
            {"error": "ticket_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ticket = Ticket.objects.get(ticket_id=UUID(ticket_id))
    except (Ticket.DoesNotExist, ValueError):
        return Response(
            {"error": "Invalid ticket"},
            status=status.HTTP_404_NOT_FOUND
        )

    if ticket.checked_in:
        return Response(
            {"error": "Already checked in"},
            status=status.HTTP_400_BAD_REQUEST
        )

  
    ticket.checked_in = True
    ticket.checked_in_at = timezone.now()
    ticket.save(update_fields=["checked_in", "checked_in_at"])

    return Response(
        {"message": "Check-in successful "},
        status=status.HTTP_200_OK
    )