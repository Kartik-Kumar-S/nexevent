from django.db import models
from django.conf import settings


class Registration(models.Model):
    STATUS_CHOICES = [
        ("WAITLISTED", "Waitlisted"),
        ("PENDING_PAYMENT", "Pending Payment"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations"
    )

    event = models.ForeignKey(
        "event_app.Event",
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    checked_in_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("student", "event")
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        student_email = getattr(self.student, "email", str(self.student))
        event_title = getattr(self.event, "title", str(self.event))
        return f"{student_email} - {event_title} ({self.status})"