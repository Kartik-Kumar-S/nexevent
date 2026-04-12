from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Registration, WaitlistEntry
from .serializers import (
    RegistrationSerializer, 
    RegistrationCreateSerializer,
    WaitlistSerializer
)
from .services import RegistrationService

class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Students see only their registrations
        if self.request.user.role == 'student':
            return Registration.objects.filter(student=self.request.user)
        # Staff see all
        return Registration.objects.all()
    
    def create(self, request):
        
        serializer = RegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = RegistrationService.register_for_event(
                event_id=serializer.validated_data['event_id'],
                student=request.user
            )
            
            if result['type'] == 'registration':
                return Response(
                    RegistrationSerializer(result['object']).data,
                    status=status.HTTP_201_CREATED
                )
            else:  # waitlist
                return Response(
                    {
                        'message': 'Event is full. You have been added to the waitlist.',
                        'waitlist': WaitlistSerializer(result['object']).data
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        
        registration = self.get_object()
        
        # Only allow cancelling your own registration
        if registration.student != request.user:
            return Response(
                {'error': 'You can only cancel your own registrations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if registration.status == 'cancelled':
            return Response(
                {'error': 'Registration already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        RegistrationService.cancel_registration(registration)
        
        return Response(
            {'message': 'Registration cancelled successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def my_registrations(self, request):
        
        registrations = Registration.objects.filter(student=request.user)
        serializer = self.get_serializer(registrations, many=True)
        return Response(serializer.data)