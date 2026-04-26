from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'transaction_id', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class PaymentIntentSerializer(serializers.Serializer):
    registration_id = serializers.UUIDField()
    client_secret = serializers.CharField()