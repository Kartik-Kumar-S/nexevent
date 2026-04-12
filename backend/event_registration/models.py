from django.db import models
from django.conf import settings
from event_app.models import Event

class Registration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
        ('checked_in', 'Checked In'),
        ('no_show', 'No Show'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title}"


class WaitlistEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waitlist')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['position', 'added_at']
        verbose_name_plural = 'Waitlist entries'
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title} (Position: {self.position})"

