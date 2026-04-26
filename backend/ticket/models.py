import uuid
from django.db import models


def ticket_upload_path(instance, filename):
    return f"tickets/{instance.ticket_id}.png"


class Ticket(models.Model):

    registration = models.OneToOneField(
        "event_registration.Registration",
        on_delete=models.CASCADE,
        related_name="ticket"
    )

    ticket_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to=ticket_upload_path)

    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.ticket_id)