from rest_framework import serializers
from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = [
            "id",
            "student",
            "event",
            "status",
            "registered_at",
            "cancelled_at",
        ]
        read_only_fields = ["student", "status", "registered_at", "cancelled_at"]