from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(source='organizer.id', read_only=True)
    organizer_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'organizer_id',
            'organizer_name',
            'title',
            'description',
            'date',
            'time',
            'location',
            'capacity',
            'category',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'organizer_id', 'organizer_name', 'created_at', 'updated_at']

    def get_organizer_name(self, obj):
        full_name = f"{obj.organizer.first_name} {obj.organizer.last_name}".strip()
        return full_name or obj.organizer.email

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        return value