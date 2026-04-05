from django.urls import path
from .views import EventListCreateView, EventDetailView

urlpatterns = [
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<uuid:pk>/', EventDetailView.as_view(), name='event-detail'),
]