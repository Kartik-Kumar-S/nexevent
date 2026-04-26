import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from .models import Ticket


def generate_ticket(registration):
    """
    Generates ticket + QR containing ONLY ticket UUID
    """

    if hasattr(registration, "ticket"):
        return registration.ticket

    ticket = Ticket.objects.create(registration=registration)

    qr = qrcode.make(str(ticket.ticket_id))

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)  

    file_name = f"{ticket.ticket_id}.png"
    ticket.qr_code.save(
        file_name,
        ContentFile(buffer.read()),
        save=False
    )

    ticket.save(update_fields=["qr_code"]) 

    buffer.close() 

    return ticket