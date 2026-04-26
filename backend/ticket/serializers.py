from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    # Generate full URL for QR code
    qr_code_url = serializers.SerializerMethodField()
    
    # Add extra useful info from Registration
    event_name = serializers.CharField(source='registration.event.title', read_only=True)
    user_name = serializers.CharField(source='registration.user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='registration.user.email', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_id',       
            'qr_code',
            'qr_code_url',
            'checked_in',      
            'created_at',
            'event_name',
            'user_name',
            'user_email'
        ]
        # These should not be edited directly via API
        read_only_fields = ['ticket_id', 'checked_in', 'created_at']

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None