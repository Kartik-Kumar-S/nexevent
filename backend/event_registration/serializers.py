from rest_framework import serializers
from event_app.models import Event
from .models import Registration, WaitlistEntry

class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = Registration
        fields = ['id', 'event', 'event_title', 'student', 'student_name', 
                  'status', 'registered_at', 'cancelled_at', 'checked_in_at']
        read_only_fields = ['student', 'status', 'registered_at', 'cancelled_at', 'checked_in_at']


class RegistrationCreateSerializer(serializers.Serializer):
    # MUST be UUIDField because your Event.id is a UUID string
    event_id = serializers.UUIDField()

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist")
        
        # use your real “open” status
        if event.status != 'published':   # not 'approved'
            raise serializers.ValidationError("Event is not approved for registration")
        
        return value


class WaitlistSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = WaitlistEntry
        fields = ['id', 'event', 'student', 'student_name', 'position', 'added_at']