from django.db import transaction
from django.utils import timezone
from .models import Registration, WaitlistEntry
from event_app.models import Event

class RegistrationService:
    
    @staticmethod
    def register_for_event(event_id, student):
        with transaction.atomic():
            # event_id is UUID, Event.id is UUIDField
            event = Event.objects.select_for_update().get(id=event_id)
            
            # status must be 'published' to accept registrations
            if event.status != 'published':
                raise ValueError("Event is not approved for registration")
            
            # already registered?
            if Registration.objects.filter(event=event, student=student).exists():
                raise ValueError("You are already registered for this event")
            
            # already on waitlist?
            if WaitlistEntry.objects.filter(event=event, student=student).exists():
                raise ValueError("You are already on the waitlist")
            
            # how many confirmed registrations?
            current_count = Registration.objects.filter(
                event=event,
                status='registered'
            ).count()
            
            # IMPORTANT: use your real capacity field name
            if current_count < event.capacity:   # field name from your JSON
                registration = Registration.objects.create(
                    event=event,
                    student=student,
                    status='registered'
                )
                return {'type': 'registration', 'object': registration}
            else:
                next_position = WaitlistEntry.objects.filter(event=event).count() + 1
                waitlist_entry = WaitlistEntry.objects.create(
                    event=event,
                    student=student,
                    position=next_position
                )
                return {'type': 'waitlist', 'object': waitlist_entry}
    
    @staticmethod
    def cancel_registration(registration):
        with transaction.atomic():
            registration.status = 'cancelled'
            registration.cancelled_at = timezone.now()
            registration.save()
            RegistrationService.promote_from_waitlist(registration.event)
            return registration
    
    @staticmethod
    def promote_from_waitlist(event):
        waitlist_entry = WaitlistEntry.objects.filter(event=event).first()
        
        if waitlist_entry:
            Registration.objects.create(
                event=event,
                student=waitlist_entry.student,
                status='registered'
            )
            
            waitlist_entry.delete()
            
            remaining = WaitlistEntry.objects.filter(event=event).order_by('position')
            for idx, entry in enumerate(remaining, start=1):
                entry.position = idx
                entry.save()
            
            return True
        return False