from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Event
from .permissions import IsOrganizerOrAdminForWrite
from .serializers import EventSerializer


class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('organizer').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrAdminForWrite]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.select_related('organizer').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrAdminForWrite]