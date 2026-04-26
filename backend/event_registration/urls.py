from django.urls import path
from .views import (
    RegisterForEventView,
    CancelRegistrationView,
    MyRegistrationsView,
    AdminEventRegistrationsView,
)

urlpatterns = [
    path("events/<uuid:event_id>/register/", RegisterForEventView.as_view()),
    path("<int:pk>/cancel/", CancelRegistrationView.as_view()),
    path("my-registrations/", MyRegistrationsView.as_view()),
    path("admin/events/<uuid:event_id>/registrations/", AdminEventRegistrationsView.as_view()),
]