from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from event_app.models import Event
from .models import Registration


SEAT_HOLDING_STATUSES = ["PENDING_PAYMENT", "CONFIRMED"]


def get_seat_holding_count(event):
    return Registration.objects.filter(
        event=event,
        status__in=SEAT_HOLDING_STATUSES
    ).count()


@transaction.atomic
def register_user_for_event(student, event_id):
    """Register student for event."""
    event = Event.objects.select_for_update().get(id=event_id)

    if hasattr(event, "is_approved") and not event.is_approved:
        raise ValidationError("Event is not approved yet.")

    if Registration.objects.filter(student=student, event=event).exists():
        raise ValidationError("Already registered.")

    occupied_seats = get_seat_holding_count(event)

    razorpay_order = None

    if occupied_seats < event.capacity:
        status = "PENDING_PAYMENT"
    else:
        status = "WAITLISTED"

    registration = Registration.objects.create(
        student=student,
        event=event,
        status=status
    )

    if status == "PENDING_PAYMENT":
        from payment.services import create_razorpay_order
        razorpay_order = create_razorpay_order(registration)

    return registration, razorpay_order


@transaction.atomic
def cancel_registration(registration):
    event = Event.objects.select_for_update().get(id=registration.event.id)

    if registration.status == "CANCELLED":
        raise ValidationError("Already cancelled.")

    was_holding_seat = registration.status in SEAT_HOLDING_STATUSES

    registration.status = "CANCELLED"
    registration.cancelled_at = timezone.now()
    registration.save(update_fields=["status", "cancelled_at"])

    
    return promote_waitlisted_user(event)

@transaction.atomic
def promote_waitlisted_user(event):
    """Promote first waitlisted student."""
    event = Event.objects.select_for_update().get(id=event.id)

    occupied_seats = get_seat_holding_count(event)

    if occupied_seats >= event.capacity:
        return None

    next_waitlisted = (
        Registration.objects
        .select_for_update()
        .filter(event=event, status="WAITLISTED")
        .order_by("registered_at")
        .first()
    )

    if not next_waitlisted:
        return None

    next_waitlisted.status = "PENDING_PAYMENT"
    next_waitlisted.save(update_fields=["status"])

    from payment.services import create_razorpay_order
    razorpay_order = create_razorpay_order(next_waitlisted)

    return next_waitlisted, razorpay_order